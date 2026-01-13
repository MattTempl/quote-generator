# Inventory Management Guide

To manage your product stock, you do not need complex software. You simply edit the master CSV file.

## How to Update Stock
1.  Open the file: `knowledge_base/sample_products.csv`
2.  Find the column named **Stock** (Column E).
3.  Change the numbers to reflect your current inventory.
4.  Save the file.
5.  **Redeploy** on Render (to load the new file).

## Example
| SKU | Name | ... | Stock |
| :--- | :--- | :--- | :--- | 
| SOFA-001 | Leather Sofa | ... | **0** | <--- Out of Stock (Bot will refuse quotes)
| SOFA-002 | Fabric Sofa | ... | **12** | <--- In Stock

## Rules
*   If `Stock` is **0**, the bot will say the item is unavailable.
*   If a user asks for **10** but you only have **5**, the bot will tell them there is not enough stock.
