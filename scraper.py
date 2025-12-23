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
import tkinter as tk
from tkinter import ttk, messagebox
import sys

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

def get_user_config():
    """
    Launch a Tkinter GUI to get search configuration from the user.
    Returns a dictionary with the configuration or None if cancelled.
    """
    config = {}
    
    def on_submit():
        config['address'] = address_entry.get().strip()
        config['keywords'] = [k.strip() for k in keywords_entry.get().split(',') if k.strip()]
        try:
            config['max_leads'] = int(max_leads_entry.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "O número de leads deve ser um valor inteiro.")
            return
            
        config['headless'] = headless_var.get()
        
        if not config['address']:
            messagebox.showerror("Erro", "A localização é obrigatória.")
            return
        if not config['keywords']:
            messagebox.showerror("Erro", "Pelo menos uma palavra-chave deve ser informada.")
            return
            
        root.destroy()

    def on_cancel():
        config.clear()
        root.destroy()
        sys.exit()

    root = tk.Tk()
    root.title("Configuração do Scraper Google Maps")
    root.geometry("500x350")
    
    # Styles
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10))
    
    # Padding
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    # Address
    ttk.Label(frame, text="Localização Alvo (Endereço Completo):").pack(anchor=tk.W, pady=(0, 5))
    address_entry = ttk.Entry(frame, width=50)
    address_entry.insert(0, "Avenida Embaixador Abelardo Bueno, 3401 – Barra Olímpica – Rio de Janeiro, RJ")
    address_entry.pack(fill=tk.X, pady=(0, 15))

    # Keywords / Niches
    ttk.Label(frame, text="Termos de Busca / Nichos / Profissões (separados por vírgula):").pack(anchor=tk.W, pady=(0, 5))
    ttk.Label(frame, text="Exemplo: restaurantes, dentistas, academias", font=('Arial', 8, 'italic'), foreground='gray').pack(anchor=tk.W, pady=(0, 5))
    keywords_entry = ttk.Entry(frame, width=50)
    keywords_entry.insert(0, "empresas, marketing, consultoria")
    keywords_entry.pack(fill=tk.X, pady=(0, 15))

    # Max Leads
    ttk.Label(frame, text="Máximo de Leads (por termo):").pack(anchor=tk.W, pady=(0, 5))
    max_leads_entry = ttk.Entry(frame, width=20)
    max_leads_entry.insert(0, "50")
    max_leads_entry.pack(anchor=tk.W, pady=(0, 15))
    
    # Headless
    headless_var = tk.BooleanVar(value=False)
    headless_check = ttk.Checkbutton(frame, text="Modo Oculto (Headless)", variable=headless_var)
    headless_check.pack(anchor=tk.W, pady=(0, 20))

    # Buttons
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill=tk.X)
    
    submit_btn = ttk.Button(btn_frame, text="Iniciar Busca", command=on_submit)
    submit_btn.pack(side=tk.RIGHT, padx=5)
    
    cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=on_cancel)
    cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    # Lift window to top
    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    
    root.mainloop()
    
    return config

if __name__ == "__main__":
    # Get configuration from GUI
    config = get_user_config()
    
    if not config:
        print("Busca cancelada pelo usuário.")
        sys.exit()
        
    print(f"Iniciando scraper com configuração: {config}")

    scraper = GoogleMapsScraper(headless=config['headless'])
    
    target_address = config['address']
    
    try:
        if scraper.search_location(target_address):
            all_leads = []
            
            for keyword in config['keywords']:
                print(f"\n--- Iniciando busca para o termo: {keyword} ---")
                scraper.search_nearby(keyword)
                leads = scraper.extract_leads(max_leads=config['max_leads'])
                
                # Add a metadata field for the source keyword
                for lead in leads:
                    lead['keyword'] = keyword
                    
                all_leads.extend(leads)
                
            # Save to Excel
            if all_leads:
                # Create filename based on first keyword or timestamp
                sanitized_key = re.sub(r'[^a-zA-Z0-9]', '_', config['keywords'][0])
                filename = f"leads_{sanitized_key}_{int(time.time())}.xlsx"
                
                df = pd.DataFrame(all_leads)
                df.to_excel(filename, index=False)
                print(f"Salvo {len(all_leads)} leads em {filename}")
                messagebox.showinfo("Concluído", f"Busca finalizada! {len(all_leads)} leads salvos em {filename}")
            else:
                print("Nenhum lead encontrado.")
                messagebox.showwarning("Aviso", "Nenhum lead encontrado para os termos pesquisados.")
    except Exception as e:
        print(f"Erro fatal: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro durante a execução: {e}")
    finally:
        scraper.close()
