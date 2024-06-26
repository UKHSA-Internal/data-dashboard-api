SEO_CHANGE_FREQUENCY: str = """
This value tells search engines how often a page’s content updates, offering a hint for crawling prioritization.
\n
**Always**: This means the page is constantly changing with important, up-to-the-minute updates. 
A subreddit index page, a stock market data page, and the index page of a major news site might use this tag.
\n
**Hourly**: The page is updated on an hourly basis or thereabouts.
 Major news sites, weather sites, and active web forums might use this tag.
\n
**Daily**: The page is updated with new content on average once a day. 
Small web forums, classified ad pages, daily newspapers, and daily blogs might use this tag for their homepage.
\n
**Weekly**: The page is updated around once a week with new content. 
Product info pages with daily pricing information, small blogs, and website directories use this tag.
\n
**Monthly**: The page is updated around once a month; maybe more, maybe less. 
Category pages, evergreen guides with updated information, and FAQs often use this tag.
\n
**Yearly**: The page is rarely updated but may receive updates once or twice a year. 
Many static pages, such as registration pages, About pages, and privacy policies, fall into this category.
\n
**Never**: The page is never going to be updated. 
Old blog entries, old news stories, and completely static pages fall into this category. 
"""

SEO_PRIORITY: str = """
This value signals the importance of a page to search engines. 
Assigning accurate priority values to key pages of your site can help search engines understand 
the structure and hierarchy of your content.
This must be a number between 0.1 - 1.0.
"""
