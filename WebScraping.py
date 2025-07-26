import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import json

BASE_URL = "https://course.mytcas.com"

async def scrape_mytcas():

    all_results = []
    search_terms = ["วิศวกรรมปัญญาประดิษฐ์"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',             
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',  
                '--disable-gpu',            
                '--window-size=1920,1080',  
            ]
        )
        page = await browser.new_page()

        for term in search_terms:
            print(f"\n--- Processing search term: '{term}' ---")
            try:
                await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Error navigating to {BASE_URL} for term '{term}': {e}")
                await page.screenshot(path=f"nav_error_{term}.png")
                continue

            search_input_locator = page.locator('input#search')
            
            if await search_input_locator.is_visible():
                await search_input_locator.fill(term)
                print(f"Filled search bar with '{term}'.")

                search_button_locator = page.locator('.i-search')
                if await search_button_locator.is_visible():
                    await search_button_locator.click()
                    print("Clicked search button.")
                else:
                    await search_input_locator.press("Enter")
                    print("Pressed Enter on search input.")

                try:
                    await page.wait_for_selector("ul.t-programs", timeout=15000)
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"Warning: Search results (ul.t-programs) did not load for '{term}' within timeout. Error: {e}")
                    await page.screenshot(path=f"search_results_load_error_{term}.png")
                    continue

                current_page_hrefs = []
                program_link_locators = await page.locator("ul.t-programs li a").all()
                
                if program_link_locators:
                    print(f"Found {len(program_link_locators)} program links for '{term}'.")
                    for link_locator in program_link_locators:
                        href = await link_locator.get_attribute("href")
                        if href:
                            current_page_hrefs.append(href)
                else:
                    print(f"No program links found on search results page for '{term}'.")
                    await page.screenshot(path=f"no_links_found_screenshot_{term}.png")
                    continue

                print(f"=== List of all hrefs collected for '{term}' ===")
                for i, href in enumerate(current_page_hrefs, 1):
                    print(f"{i}. {href}")

                for i, href in enumerate(current_page_hrefs):
                    if not href.strip():
                        continue

                    detail_url = BASE_URL + href.strip()
                    print(f"  [{i+1}/{len(current_page_hrefs)}] Scraping detail: {detail_url}")

                    try:
                        await page.goto(detail_url, wait_until="networkidle", timeout=60000)
                        await page.wait_for_timeout(1500)

                        program_data = {"search_term": term, "url": detail_url}

                        try:
                            university_locator = page.locator('a[href^="/universities/"]').first
                            program_data['university'] = await university_locator.text_content(timeout=5000)
                        except Exception:
                            program_data['university'] = ""

                        try:
                            faculty_locator = page.locator('a[href*="/faculties/"]').first
                            program_data['faculty'] = await faculty_locator.text_content(timeout=5000)
                        except Exception:
                            program_data['faculty'] = ""

                        try:
                            field_locator = page.locator('a[href*="/fields/"]').first
                            program_data['field'] = await field_locator.text_content(timeout=5000)
                        except Exception:
                            program_data['field'] = ""

                        program_title_text = "N/A" # Default value
                       
                        try:
                            program_title_locator_specific = page.locator('h1.h-program-name').first
                            await program_title_locator_specific.wait_for(state='visible', timeout=5000) # Wait for it
                            program_title_text = (await program_title_locator_specific.text_content()).strip()
                            print(f"  Found Program Title (specific): '{program_title_text}'")
                        except Exception:
                            
                            try:
                                program_title_locator_general_h1 = page.locator('h1').first
                                await program_title_locator_general_h1.wait_for(state='visible', timeout=5000)
                                program_title_text = (await program_title_locator_general_h1.text_content()).strip()
                                print(f"  Found Program Title (general h1): '{program_title_text}'")
                            except Exception:
                                page_title_from_tag = await page.title()
                                if page_title_from_tag:
                                    program_title_text = page_title_from_tag.replace(' - MyTCAS', '').strip()
                                    print(f"  Found Program Title (from page title tag): '{program_title_text}'")
                                else:
                                    print(f"  Warning: Program Title not found through any method for {detail_url}.")

                        program_data['Program Title'] = program_title_text
                            
                        dt_dd = {}
                        dt_elements = await page.locator("ul.body.t-program dt").all()
                        dd_elements = await page.locator("ul.body.t-program dd").all()

                        for dt_elem, dd_elem in zip(dt_elements, dd_elements):
                            dt_text = (await dt_elem.text_content()).strip() 
                            dd_text = (await dd_elem.text_content()).strip()
                            if dt_text and dd_text:
                                dt_dd[dt_text] = dd_text
                        
                        program_data["details"] = dt_dd
                        all_results.append(program_data)
                        print(f"  Extracted {len(dt_dd)} detail items for '{program_data['Program Title']}'.")

                    except Exception as e:
                        print(f"  Failed to scrape details from {detail_url}: {e}")
                        await page.screenshot(path=f"error_detail_screenshot_{term}_{i}.png")
                        continue

            else:
                print(f"Search input ('input#search') not found on homepage for term: '{term}'. Check selector or page load.")
                await page.screenshot(path=f"no_search_input_screenshot_{term}.png")

        await browser.close()

    output_dir = Path("data")
    output_dir.mkdir(parents=True, exist_ok=True) 
    output_path = output_dir / "course_data.json"
    
    output_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDONE! Saved all collected data to {output_path.absolute()} with {len(all_results)} entries.")

if __name__ == "__main__":
    Path("data/web_scraping").mkdir(parents=True, exist_ok=True)
    asyncio.run(scrape_mytcas())