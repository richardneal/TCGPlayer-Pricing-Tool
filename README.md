# TCGPlayer Pricing Tool
Basic pricing tool to be used with CSVs exported from TCGPlayer's pricing page. 
This is mostly meant as a starting point for any sellers looking to automate their pricing, so while it can be used as is, it ideally is extensible enough for
someone with a small amount of Python knowledge to modify the pricing heuristics to their liking. 

# Requirements
This tool requires Python >= 3.8 and the above CSV export.

# Usage
After cloning the repository, in that directory, run `python3 reprice_csv.py <path_to_tcgplayer_export.csv>`. 
That will reprice all products provided from the input CSV (without modifying it) using the following logic, which likely makes the most sense for TCG Direct sellers, but again, feel free to modify:
1. If the product has a TCG Direct Low price or is sealed, set its price to the higher of TCG Direct Low or TCG Low + Shipping.
2. If neither of those are true, if the product has a TCG Low + Shipping price, set its price to 1.1 x that price, rounded to 99 cents.
3. If none of the above are true, which should mean the product has no comparable products on TCGPlayer, set its price to $999.99 and output a warning to reprice it manually.

It will then output a new CSV with the new prices, which will have the same name, but appended with "_OUTPUT"

# License
This project is licensed under BSD, the terms and details of which can be found in LICENSE.

# Support
This project is provided as-is. If you encounter bugs or areas that could be improved, do feel free to file an issue or pull request,
and while I intend to improve the code going forward for my own use (and for others, as time permits), there are no promises
made about that. Additionally, there are no guarantees that this won't reprice products in ways that don't make sense
for you as a seller, so be sure to validate the output before uploading it back to TCGPlayer.