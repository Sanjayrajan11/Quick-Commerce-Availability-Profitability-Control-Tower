# Two-minute interview explanation
I built SwiftCart as a synthetic quick-commerce portfolio project to understand how availability problems affect both customer service and contribution profit. It is not based on a real company’s transactions.

I started by identifying the different decisions that operations, supply chain, category managers and finance would need to make. I documented requirements, user stories, process maps and KPI definitions. One important distinction was that opening stock availability is not the same as the proportion of requested units fulfilled.

I generated 300,000 linked orders with Python. Demand depletes stock, receipts replenish it, and accepted substitutions consume replacement inventory. I also injected controlled data-quality problems so I could build and demonstrate an audited cleaning process.

The data is loaded into SQLite with foreign keys. I wrote 48 business SQL queries, including window functions and cohort analysis. A shared Python KPI layer calculates availability, estimated lost demand and the contribution bridge. I reconciled the SQL and Python financial totals rather than allowing each dashboard to define its own numbers.

For inventory, I used trailing demand, supplier lead time and safety stock to explain reorder suggestions. I compared four simple forecasting methods using chronological validation and test periods. The risk and action engines turn those calculations into evidence, suggested owners and next steps.

The Streamlit application has fourteen operational workspaces, a scenario lab and a separate synthetic live event simulation. Automated tests cover both calculations and interactions. Browser visual testing is still pending because the available automation was blocked, and I am explicit about that. The project taught me to defend assumptions and trace a recommendation back to data instead of just making charts.
