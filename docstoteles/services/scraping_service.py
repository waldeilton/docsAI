import os
import logging
import time
import requests
from firecrawl import FirecrawlApp
import os
from core.config import APP_CONFIG, PATHS
from core.database import ScrapingProjectManager
import shutil

logger = logging.getLogger(__name__)

class ScrapingService:
    """Service for web scraping operations"""
    
    def __init__(self, api_key=None, api_url=None):
        """Initialize the scraping service"""
        self.api_key = api_key or APP_CONFIG["firecrawl_api_key"]
        self.api_url = api_url or APP_CONFIG["firecrawl_api_url"]
        self.project_manager = ScrapingProjectManager()
        
        # Initialize FirecrawlApp
        self.app = FirecrawlApp(api_key=self.api_key, api_url=self.api_url)
        logger.info(f"Scraping service initialized with API URL: {self.api_url}")
    
    def map_url(self, url):
        """Map a URL to extract all links"""
        try:
            logger.info(f"Starting MAP for URL: {url}")
            map_result = self.app.map_url(url)
            
            links = map_result.get("links", [])
            if not links:
                logger.error("No links found from MAP!")
                raise Exception("No links found from MAP!")
            
            logger.info(f"Number of links found: {len(links)}")
            return links
        except Exception as e:
            logger.error(f"Error executing MAP: {str(e)}")
            raise
    
    def fetch_next_data(self, url):
        """Fetch the next chunk of results using the URL 'next'"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def batch_scrape_urls(self, links, formats=None):
        """Scrape a batch of URLs and return the content"""
        if formats is None:
            formats = ['markdown']
            
        scrape_params = {'formats': formats}
        
        try:
            logger.info(f"Starting batch scrape with {len(links)} links")
            batch_scrape_result = self.app.batch_scrape_urls(links, scrape_params)
            
            # Handle pagination of results
            all_scrape_data = []
            response = batch_scrape_result
            
            while True:
                data_chunk = response.get("data", [])
                all_scrape_data.extend(data_chunk)
                
                next_url = response.get("next")
                if not next_url:
                    break
                    
                logger.debug("Fetching next chunk of results for batch scrape...")
                response = self.fetch_next_data(next_url)
            
            logger.info(f"Total scraped pages: {len(all_scrape_data)}")
            return all_scrape_data
        except Exception as e:
            logger.error(f"Error during batch scrape: {str(e)}")
            raise
    
    def save_scraped_content(self, scraped_data, project_name):
        """Save scraped content to the specified project directory"""
        # Create output directory
        output_dir = os.path.join(PATHS["rag_directory"], project_name)
        
        # If directory exists, delete it first
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")
        
        saved_files = 0
        for idx, page in enumerate(scraped_data, start=1):
            markdown_content = page.get("markdown")
            if not markdown_content:
                logger.warning(f"Page {idx} does not contain markdown content. Skipping.")
                continue
                
            file_path = os.path.join(output_dir, f"{idx}.md")
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(markdown_content)
                logger.info(f"File saved successfully: {file_path}")
                saved_files += 1
            except Exception as e:
                logger.error(f"Error saving file {file_path}: {str(e)}")
    
    def run_full_scraping_process(self, url, project_name, progress_callback=None):
        """Run the complete scraping process for a URL"""
        try:
            # Update progress
            if progress_callback:
                progress_callback(0.1, "Mapping URL to extract links...")
            
            # Map URL to extract links
            links = self.map_url(url)
            
            # Update progress
            if progress_callback:
                progress_callback(0.3, f"Found {len(links)} links. Starting scraping...")
            
            # Scrape links
            scraped_data = self.batch_scrape_urls(links)
            
            # Update progress
            if progress_callback:
                progress_callback(0.8, f"Scraped {len(scraped_data)} pages. Saving content...")
            
            # Save content
            saved_files = self.save_scraped_content(scraped_data, project_name)
            
            # Save project record
            self.project_manager.save_project(
                project_name=project_name,
                source_url=url,
                file_count=saved_files
            )
            
            # Update progress
            if progress_callback:
                progress_callback(1.0, f"Completed! Saved {saved_files} files to {project_name}")
            
            return {
                "success": True,
                "project_name": project_name,
                "url": url,
                "files_saved": saved_files
            }
            
        except Exception as e:
            logger.error(f"Error in scraping process: {str(e)}")
            if progress_callback:
                progress_callback(1.0, f"Error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }