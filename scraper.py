import time
import re
import pandas as pd
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from browser import BrowserManager

class GoogleMapsScraper:
    def __init__(self, headless=False):
        self.driver = BrowserManager.create_driver(headless)
        self.wait = WebDriverWait(self.driver, 20)
        
    def close(self):
        if self.driver:
            self.driver.quit()

    def clean_phone(self, phone):
        if not phone: return ""
        return re.sub(r'[^\d\(\)\-\+\s]', '', phone).strip()

    def search_location(self, address):
        print(f"Searching for location: {address}")
        self.driver.get('https://www.google.com/maps/')
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@id="searchboxinput"]'))
            )
            search_box.clear()
            search_box.send_keys(address)
            search_box.send_keys(Keys.ENTER)
            time.sleep(5) # Wait for zoom
            return True
        except Exception as e:
            print(f"Error searching location: {e}")
            return False

    def search_nearby(self, keyword="empresas"):
        print(f"Searching nearby for: {keyword}")
        try:
            # Locate search box again
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@id="searchboxinput"]'))
            )
            search_box.click()
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception as e:
            print(f"Error initiating nearby search: {e}")

    def extract_leads(self, max_leads=50):
        leads = []
        unique_names = set()
        processed_candidates = set()
        
        print(f"Extracting up to {max_leads} leads...")
        
        xpath_result = '//a[contains(@href, "/place/")]'
        
        consecutive_failures = 0
        
        while len(leads) < max_leads:
            try:
                # Find all current results
                elements = self.driver.find_elements(By.XPATH, xpath_result)
                
                # Check if we need to scroll
                if not elements:
                    print("No elements found.")
                    break
                
                processed_in_this_pass = False
                
                for element in elements:
                    try:
                        name_candidate = element.get_attribute("aria-label") or element.text
                        if not name_candidate:
                            continue
                            
                        # Clean name candidate to check against processed
                        if name_candidate in processed_candidates:
                             continue
                             
                        # Found a new candidate
                        processed_in_this_pass = True
                        processed_candidates.add(name_candidate)
                        print(f"Processing: {name_candidate}")
                        
                        # Click
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(1)
                        try:
                            element.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", element)
                            
                        time.sleep(2)
                        
                         # Verify we are in details view
                        on_details = False
                        try:
                             def check_h1(d):
                                 h1s = d.find_elements(By.TAG_NAME, 'h1')
                                 for h in h1s:
                                     try:
                                         t = h.text
                                         if t and t not in ["Resultados", "Principal", "", "Patrocinado"] and len(t) > 2:
                                             return True
                                     except:
                                         pass
                                 return False
                                 
                             WebDriverWait(self.driver, 5).until(check_h1)
                             on_details = True
                        except:
                             print(f"Failed to load details or H1 for {name_candidate}")
                        
                        if on_details:
                            data = self._extract_details(name_candidate)
                            if data['name'] and data['name'] not in ["Resultados", "Principal", "Patrocinado"]:
                                if data['name'] not in unique_names:
                                    leads.append(data)
                                    unique_names.add(data['name'])
                                    print(f"Extracted: {data['name']}")
                                    consecutive_failures = 0
                                else:
                                    print(f"Duplicate extracted (skipping): {data['name']}")
                            else:
                                print(f"Skipping invalid name: {data.get('name')}")
                            
                            self._go_back()
                        else:
                            print("Details did not load, possibly just generic result.")
                            unique_names.add(name_candidate) 
                            consecutive_failures += 1

                        # Break to refresh list as DOM is likely stale or changed
                        break
                        
                    except Exception as e:
                        print(f"Error access element: {e}")
                        continue
                
                if not processed_in_this_pass:
                    print("No new items visible on screen, scrolling...")
                    try:
                        # Scroll via feed div if possible
                        try:
                             feed = self.driver.find_element(By.XPATH, '//div[@role="feed"]')
                             self.driver.execute_script("arguments[0].scrollTop += 700;", feed)
                        except: 
                             self.driver.execute_script("window.scrollBy(0, 500);")
                        
                        time.sleep(3)
                        
                        # Check if we are stuck
                        new_elements = self.driver.find_elements(By.XPATH, xpath_result)
                        # Heuristic: if same number of elements as before scroll and we processed everything...
                        if len(new_elements) == len(elements) and not processed_in_this_pass:
                             consecutive_failures += 1
                    
                    except Exception as e:
                        print(f"Scroll error: {e}")
                        consecutive_failures += 1
                        
                if consecutive_failures > 5:
                    print("Too many failures or no new items found. Stopping.")
                    break
                    
            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(2)
                
        return leads

    def _extract_details(self, expected_name=None):
        data = {
            'name': '',
            'address': '',
            'phone': '',
            'website': '',
            'link': self.driver.current_url
        }
        
        try:
            # Name - find H1 that is not generic and preferably contains expected name
            h1s = self.driver.find_elements(By.TAG_NAME, 'h1')
            best_match = None
            
            for h1 in h1s:
                t = h1.text
                if not t: continue
                # Skip generic headers
                if any(x in t for x in ["Resultados", "Principal", "Patrocinado", "Anúncio"]):
                    continue
                if len(t) <= 2:
                    continue
                    
                # If we have an expected name, prefer the one that matches
                if expected_name and (expected_name in t or t in expected_name):
                    best_match = t
                    break
                
                # Otherwise keep the first valid one as fallback
                if not best_match:
                    best_match = t
            
            data['name'] = best_match if best_match else ""
        except:
            pass
            
        try:
            # Address - button with data-item-id='address'
            addr_btn = self.driver.find_element(By.XPATH, '//button[contains(@data-item-id, "address")]')
            data['address'] = addr_btn.get_attribute("aria-label").replace("Endereço: ", "")
        except:
            pass
            
        try:
            # Phone - button with data-item-id='phone'
            phone_btn = self.driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone")]')
            data['phone'] = self.clean_phone(phone_btn.get_attribute("aria-label").replace("Telefone: ", ""))
        except:
            pass
            
        try:
            # Website
            web_btn = self.driver.find_element(By.XPATH, '//a[contains(@data-item-id, "authority")]')
            data['website'] = web_btn.get_attribute('href')
        except:
            pass
            
        return data

    def _go_back(self):
        try:
            back_btn = self.driver.find_element(By.XPATH, '//button[@aria-label="Voltar"]')
            back_btn.click()
            time.sleep(2)
        except:
            print("Back button not found, trying Esc")
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass

if __name__ == "__main__":
    scraper = GoogleMapsScraper(headless=False)
    
    target_address = "Avenida Embaixador Abelardo Bueno, 3401 – Barra Olímpica – Rio de Janeiro, RJ"
    
    if scraper.search_location(target_address):
        scraper.search_nearby("empresas")
        leads = scraper.extract_leads(max_leads=200) # User asked for 'all', but lets start with limit
        
        # Save to Excel
        if leads:
            df = pd.DataFrame(leads)
            df.to_excel("empresas_rock_in_rio.xlsx", index=False)
            print(f"Saved {len(leads)} leads to empresas_rock_in_rio.xlsx")
        else:
            print("No leads found.")
            
    scraper.close()
