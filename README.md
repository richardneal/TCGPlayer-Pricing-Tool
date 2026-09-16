# TCGPlayer Pricing Tool
Basic pricing tool to be used with CSVs exported from TCGPlayer's pricing page. 
This is mostly meant as a starting point for any sellers looking to automate their pricing, so while it can be used as is, it ideally is extensible enough for
someone with a small amount of Python knowledge to modify the pricing heuristics to their liking. 

# Requirements
This tool requires Python >= 3.9 and the above CSV export. It uses only the standard library, so there is nothing to install.

# Installing
Neither script has to be installed: `python3 reprice_csv.py <export.csv>` works from the repository, and from anywhere if
you give the full path to the script. To run them by name from any directory, symlink them somewhere on your `PATH`:

```
mkdir -p ~/.local/bin
ln -s "$PWD/reprice_csv.py" ~/.local/bin/tcg-reprice
ln -s "$PWD/sorted_cards.py" ~/.local/bin/tcg-list
```

The symlinks point back at your checkout, so they pick up any changes you make. If `~/.local/bin` is not already on your
`PATH`, add it in your shell's startup file.

# Usage
Both scripts take the path to a TCGPlayer export, and fall back to `TCG.csv` in the current directory if you do not pass
one. Passing a path that does not exist is an error rather than a silent fall back, so you always know which file was read.
Pass `--latest` instead of a path to read the most recent `TCGplayer*MyPricing*.csv` in your `~/Downloads`, which saves
typing out a timestamped export name; it prints which file it picked. Pass `--help` to either script for the full usage.

## Repricing
After cloning the repository, in that directory, run `python3 reprice_csv.py <path_to_tcgplayer_export.csv>` (or `tcg-reprice`, if you set up the symlink above). 
That will reprice all products provided from the input CSV (without modifying it) using the following logic, which likely makes the most sense for TCG Direct sellers, but again, feel free to modify:
1. If the product has a TCG Direct Low price or is sealed, set its price to the higher of TCG Direct Low or TCG Low + Shipping.
2. If neither of those are true, if the product has a TCG Low + Shipping price, set its price to 1.1 x that price, rounded to 99 cents.
3. If none of the above are true, which should mean the product has no comparable products on TCGPlayer, leave the price
   you already had alone. Only a product with no price at all is given $999.99, along with a warning, so that it is easy
   to find and correct in the output CSV rather than being listed at a price you did not choose.

Each repriced product that you have in stock is logged with its new price and the percent change from the old one, and the
total value of your inventory is printed before and after repricing so you can see the overall effect at a glance.

As a safety net, a reprice that would move a price by more than 50% is reported and skipped rather than applied, so that
one bad day of TCGPlayer data cannot rewrite your whole inventory unattended. Those products are listed for you to review
by hand. Use `--max-change <percent>` to tighten or loosen that, or `--no-max-change` to apply every reprice however large.

A few other options are worth knowing:
- `--markup <multiplier>` changes the 1.1 in rule 2, so `--markup 1.25` prices those products at 1.25 x TCG Low + Shipping.
- `--show-out-of-stock` also reports products you hold none of. They are always repriced, so their price is current when you
  restock, but they are left out of the log by default because they tend to outnumber the ones you actually have.
- `-o/--output <file>` writes the repriced CSV somewhere other than next to the input, which is worth using with `--latest`
  so you do not leave output CSVs in your downloads folder.

It will then output a new CSV with the new prices, which will have the same name, but appended with "_OUTPUT"

## Listing your inventory
Run `python3 sorted_cards.py <path_to_tcgplayer_export.csv>` (or `tcg-list`) to print the total value of your inventory, followed by every
product you have in stock sorted from most to least expensive. This one is read-only; it never writes a CSV, so it is a safe
way to look over an export before or after repricing it.

# License
This project is licensed under BSD, the terms and details of which can be found in LICENSE.

# Support
This project is provided as-is. If you encounter bugs or areas that could be improved, do feel free to file an issue or pull request,
and while I intend to improve the code going forward for my own use (and for others, as time permits), there are no promises
made about that. Additionally, there are no guarantees that this won't reprice products in ways that don't make sense
for you as a seller, so be sure to validate the output before uploading it back to TCGPlayer.
