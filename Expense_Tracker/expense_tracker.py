"""
=============================================================
  EXPENSE TRACKER - CLI Application
  Author  : Built with Python Standard Libraries only
  Storage : CSV file (expenses.csv)
  Run     : python expense_tracker.py
=============================================================
"""

import csv
import os
import sys
from datetime import datetime

# ── Constants ──────────────────────────────────────────────
CSV_FILE = "expenses.csv"
FIELDNAMES = ["id", "date", "amount", "category", "description"]

CATEGORIES = [
    "Food", "Transport", "Shopping", "Health",
    "Entertainment", "Education", "Utilities", "Other"
]

# ── ANSI Color Codes (works on most terminals) ─────────────
class Color:
    HEADER  = "\033[95m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    BOLD    = "\033[1m"
    RESET   = "\033[0m"


# ══════════════════════════════════════════════════════════
#  FILE HANDLING
# ══════════════════════════════════════════════════════════

def initialize_csv():
    """
    Create the CSV file with headers if it doesn't exist.
    Called once at startup.
    """
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        print(f"{Color.GREEN}[INFO] '{CSV_FILE}' created successfully.{Color.RESET}")


def read_all_expenses():
    """
    Read all rows from CSV and return as a list of dicts.
    Returns an empty list if file has no data.
    """
    expenses = []
    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expenses.append(row)
    return expenses


def write_all_expenses(expenses):
    """
    Overwrite the entire CSV file with given list of expense dicts.
    Used by edit and delete operations.
    """
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


def get_next_id(expenses):
    """
    Generate the next integer ID based on current max ID.
    Starts from 1 if no records exist.
    """
    if not expenses:
        return 1
    # Find max ID safely (handle corrupted rows)
    ids = []
    for e in expenses:
        try:
            ids.append(int(e["id"]))
        except (ValueError, KeyError):
            pass
    return max(ids) + 1 if ids else 1


# ══════════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ══════════════════════════════════════════════════════════

def print_separator(char="─", length=72):
    print(Color.CYAN + char * length + Color.RESET)


def print_table_header():
    """Print the column header row for expense tables."""
    print_separator()
    print(
        f"{Color.BOLD}"
        f"{'ID':<5} {'Date':<12} {'Amount':>10} {'Category':<15} {'Description':<25}"
        f"{Color.RESET}"
    )
    print_separator()


def print_expense_row(expense):
    """Print a single expense row in tabular format."""
    desc = expense.get("description", "")[:24]  # Truncate long descriptions
    amount_str = f"৳{float(expense['amount']):,.2f}"
    print(
        f"{expense['id']:<5} "
        f"{expense['date']:<12} "
        f"{amount_str:>10} "
        f"{expense['category']:<15} "
        f"{desc:<25}"
    )


def clear_screen():
    """Clear terminal screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    """Print the app title banner."""
    clear_screen()
    print(Color.BOLD + Color.CYAN)
    print("╔══════════════════════════════════════╗")
    print("║        💰  EXPENSE TRACKER  💰        ║")
    print("╚══════════════════════════════════════╝")
    print(Color.RESET)


# ══════════════════════════════════════════════════════════
#  INPUT VALIDATION HELPERS
# ══════════════════════════════════════════════════════════

def get_valid_date(prompt="Enter date (YYYY-MM-DD): "):
    """
    Prompt user for a date string.
    Keep asking until a valid YYYY-MM-DD date is entered.
    """
    while True:
        raw = input(prompt).strip()
        if raw == "":
            # Default to today if blank
            return datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(f"{Color.RED}[ERROR] Invalid date. Use YYYY-MM-DD format (e.g. 2025-07-15).{Color.RESET}")


def get_valid_amount(prompt="Enter amount: ৳"):
    """
    Prompt user for a positive numeric amount.
    Rejects letters, negatives, and zero.
    """
    while True:
        raw = input(prompt).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print(f"{Color.RED}[ERROR] Amount must be greater than 0.{Color.RESET}")
                continue
            return round(amount, 2)
        except ValueError:
            print(f"{Color.RED}[ERROR] Invalid amount. Enter a number (e.g. 250 or 99.50).{Color.RESET}")


def get_valid_category(prompt="Choose category: "):
    """
    Show numbered list of categories and return the selected one.
    """
    print("\nAvailable categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {Color.YELLOW}{i}{Color.RESET}. {cat}")
    while True:
        raw = input(prompt).strip()
        try:
            choice = int(raw)
            if 1 <= choice <= len(CATEGORIES):
                return CATEGORIES[choice - 1]
            print(f"{Color.RED}[ERROR] Enter a number between 1 and {len(CATEGORIES)}.{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}[ERROR] Enter the category number, not text.{Color.RESET}")


# ══════════════════════════════════════════════════════════
#  CORE FEATURE FUNCTIONS
# ══════════════════════════════════════════════════════════

def add_expense():
    """
    Collect expense details from user and append to CSV.
    Fields: date, amount, category, description (optional).
    """
    print(f"\n{Color.BOLD}{Color.GREEN}── ADD NEW EXPENSE ──{Color.RESET}")
    print(f"{Color.CYAN}(Press Enter to use today's date){Color.RESET}")

    date        = get_valid_date()
    amount      = get_valid_amount()
    category    = get_valid_category()
    description = input("Enter description (optional, press Enter to skip): ").strip()

    # Load existing data to determine next ID
    expenses = read_all_expenses()
    new_id   = get_next_id(expenses)

    new_expense = {
        "id"          : new_id,
        "date"        : date,
        "amount"      : amount,
        "category"    : category,
        "description" : description
    }

    # Append single row to CSV without rewriting the whole file
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(new_expense)

    print(f"\n{Color.GREEN}✔ Expense added successfully! (ID: {new_id}){Color.RESET}")
    input("\nPress Enter to return to menu...")


def view_expenses():
    """
    Display all expenses in a tabular CLI format.
    Shows total at the bottom.
    """
    print(f"\n{Color.BOLD}{Color.BLUE}── ALL EXPENSES ──{Color.RESET}")

    expenses = read_all_expenses()

    if not expenses:
        print(f"{Color.YELLOW}[INFO] No expenses found. Add one first!{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    print_table_header()
    total = 0.0

    for expense in expenses:
        try:
            print_expense_row(expense)
            total += float(expense["amount"])
        except (ValueError, KeyError):
            # Skip corrupted rows silently
            print(f"{Color.RED}[WARN] Skipped corrupted row: {expense}{Color.RESET}")

    print_separator()
    print(f"{Color.BOLD}{'TOTAL':<30} ৳{total:>10,.2f}{Color.RESET}")
    print_separator()
    print(f"\n{Color.CYAN}Total Records: {len(expenses)}{Color.RESET}")
    input("\nPress Enter to return to menu...")


def filter_by_category():
    """
    Show expenses belonging to a selected category.
    Prints filtered list + subtotal.
    """
    print(f"\n{Color.BOLD}{Color.BLUE}── FILTER BY CATEGORY ──{Color.RESET}")

    category = get_valid_category()
    expenses = read_all_expenses()

    # Filter rows matching chosen category (case-insensitive)
    filtered = [e for e in expenses if e.get("category", "").lower() == category.lower()]

    if not filtered:
        print(f"{Color.YELLOW}[INFO] No expenses found for category: {category}{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    print(f"\n{Color.BOLD}Results for: {Color.GREEN}{category}{Color.RESET}")
    print_table_header()

    total = 0.0
    for expense in filtered:
        try:
            print_expense_row(expense)
            total += float(expense["amount"])
        except (ValueError, KeyError):
            pass

    print_separator()
    print(f"{Color.BOLD}{'SUBTOTAL':<30} ৳{total:>10,.2f}{Color.RESET}")
    print_separator()
    input("\nPress Enter to return to menu...")


def monthly_summary():
    """
    Ask user for year + month, then show:
    - Category-wise spending breakdown
    - Grand total for that month
    """
    print(f"\n{Color.BOLD}{Color.BLUE}── MONTHLY SUMMARY ──{Color.RESET}")

    # Get valid year
    while True:
        year_raw = input("Enter year (e.g. 2025): ").strip()
        try:
            year = int(year_raw)
            if 2000 <= year <= 2100:
                break
            print(f"{Color.RED}[ERROR] Enter a realistic year (2000–2100).{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}[ERROR] Year must be a number.{Color.RESET}")

    # Get valid month
    while True:
        month_raw = input("Enter month (1–12): ").strip()
        try:
            month = int(month_raw)
            if 1 <= month <= 12:
                break
            print(f"{Color.RED}[ERROR] Month must be between 1 and 12.{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}[ERROR] Month must be a number.{Color.RESET}")

    expenses = read_all_expenses()

    # Filter by year-month match
    month_str = f"{year}-{month:02d}"  # e.g. "2025-07"
    monthly   = [e for e in expenses if e.get("date", "").startswith(month_str)]

    month_name = datetime(year, month, 1).strftime("%B %Y")
    print(f"\n{Color.BOLD}Summary for: {Color.GREEN}{month_name}{Color.RESET}")

    if not monthly:
        print(f"{Color.YELLOW}[INFO] No expenses recorded for {month_name}.{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    # Build category-wise totals using a plain dict
    category_totals = {}
    grand_total = 0.0

    for expense in monthly:
        try:
            cat    = expense.get("category", "Uncategorized")
            amount = float(expense["amount"])
            category_totals[cat] = category_totals.get(cat, 0.0) + amount
            grand_total += amount
        except (ValueError, KeyError):
            pass

    # Display breakdown table
    print_separator()
    print(f"{Color.BOLD}{'Category':<20} {'Spent':>12} {'% of Total':>12}{Color.RESET}")
    print_separator()

    # Sort by amount descending
    for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (total / grand_total * 100) if grand_total > 0 else 0
        bar = "█" * int(pct / 5)  # Simple ASCII bar (max 20 blocks)
        print(f"{cat:<20} ৳{total:>10,.2f}   {pct:>5.1f}%  {Color.GREEN}{bar}{Color.RESET}")

    print_separator()
    print(f"{Color.BOLD}{'GRAND TOTAL':<20} ৳{grand_total:>10,.2f}{Color.RESET}")
    print_separator()
    print(f"\n{Color.CYAN}Total Transactions: {len(monthly)}{Color.RESET}")
    input("\nPress Enter to return to menu...")


def delete_expense():
    """
    Let user pick an expense by ID and permanently remove it.
    Asks for confirmation before deleting.
    """
    print(f"\n{Color.BOLD}{Color.RED}── DELETE EXPENSE ──{Color.RESET}")

    expenses = read_all_expenses()

    if not expenses:
        print(f"{Color.YELLOW}[INFO] No expenses to delete.{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    # Show full list so user can see IDs
    print_table_header()
    for expense in expenses:
        print_expense_row(expense)
    print_separator()

    # Get ID to delete
    while True:
        raw = input("\nEnter ID to delete (or 0 to cancel): ").strip()
        try:
            target_id = int(raw)
            break
        except ValueError:
            print(f"{Color.RED}[ERROR] Enter a valid numeric ID.{Color.RESET}")

    if target_id == 0:
        print("Cancelled.")
        input("\nPress Enter to return to menu...")
        return

    # Find the matching row
    target = next((e for e in expenses if int(e["id"]) == target_id), None)

    if not target:
        print(f"{Color.RED}[ERROR] No expense found with ID {target_id}.{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    # Confirm deletion
    print(f"\n{Color.YELLOW}About to delete:{Color.RESET}")
    print_table_header()
    print_expense_row(target)
    print_separator()

    confirm = input(f"{Color.RED}Are you sure? (yes/no): {Color.RESET}").strip().lower()
    if confirm in ("yes", "y"):
        updated = [e for e in expenses if int(e["id"]) != target_id]
        write_all_expenses(updated)
        print(f"{Color.GREEN}✔ Expense ID {target_id} deleted.{Color.RESET}")
    else:
        print("Deletion cancelled.")

    input("\nPress Enter to return to menu...")


def edit_expense():
    """
    Let user select an expense by ID and update any of its fields.
    Keeps old value if user presses Enter without typing.
    """
    print(f"\n{Color.BOLD}{Color.YELLOW}── EDIT EXPENSE ──{Color.RESET}")

    expenses = read_all_expenses()

    if not expenses:
        print(f"{Color.YELLOW}[INFO] No expenses to edit.{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    # Show full list so user can see IDs
    print_table_header()
    for expense in expenses:
        print_expense_row(expense)
    print_separator()

    # Get ID to edit
    while True:
        raw = input("\nEnter ID to edit (or 0 to cancel): ").strip()
        try:
            target_id = int(raw)
            break
        except ValueError:
            print(f"{Color.RED}[ERROR] Enter a valid numeric ID.{Color.RESET}")

    if target_id == 0:
        print("Cancelled.")
        input("\nPress Enter to return to menu...")
        return

    # Find matching expense
    target_index = next(
        (i for i, e in enumerate(expenses) if int(e["id"]) == target_id), None
    )

    if target_index is None:
        print(f"{Color.RED}[ERROR] No expense found with ID {target_id}.{Color.RESET}")
        input("\nPress Enter to return to menu...")
        return

    expense = expenses[target_index]

    print(f"\n{Color.CYAN}Editing ID {target_id}. Press Enter to keep current value.{Color.RESET}\n")

    # ── Date ──
    print(f"Current date: {Color.YELLOW}{expense['date']}{Color.RESET}")
    new_date_raw = input("New date (YYYY-MM-DD) or Enter to keep: ").strip()
    if new_date_raw:
        try:
            datetime.strptime(new_date_raw, "%Y-%m-%d")
            expense["date"] = new_date_raw
        except ValueError:
            print(f"{Color.RED}[WARN] Invalid date format. Keeping original.{Color.RESET}")

    # ── Amount ──
    print(f"Current amount: {Color.YELLOW}৳{expense['amount']}{Color.RESET}")
    new_amount_raw = input("New amount or Enter to keep: ৳").strip()
    if new_amount_raw:
        try:
            new_amount = float(new_amount_raw)
            if new_amount <= 0:
                print(f"{Color.RED}[WARN] Amount must be > 0. Keeping original.{Color.RESET}")
            else:
                expense["amount"] = round(new_amount, 2)
        except ValueError:
            print(f"{Color.RED}[WARN] Invalid amount. Keeping original.{Color.RESET}")

    # ── Category ──
    print(f"Current category: {Color.YELLOW}{expense['category']}{Color.RESET}")
    change_cat = input("Change category? (yes/no): ").strip().lower()
    if change_cat in ("yes", "y"):
        expense["category"] = get_valid_category()

    # ── Description ──
    print(f"Current description: {Color.YELLOW}{expense.get('description', '')}{Color.RESET}")
    new_desc = input("New description or Enter to keep: ").strip()
    if new_desc:
        expense["description"] = new_desc

    # Save changes
    expenses[target_index] = expense
    write_all_expenses(expenses)
    print(f"\n{Color.GREEN}✔ Expense ID {target_id} updated successfully!{Color.RESET}")
    input("\nPress Enter to return to menu...")


# ══════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════

def show_menu():
    """Print the main navigation menu."""
    print(f"\n{Color.BOLD}{'─'*40}{Color.RESET}")
    print(f"  {Color.CYAN}1.{Color.RESET} ➕  Add Expense")
    print(f"  {Color.CYAN}2.{Color.RESET} 📋  View All Expenses")
    print(f"  {Color.CYAN}3.{Color.RESET} 🔍  Filter by Category")
    print(f"  {Color.CYAN}4.{Color.RESET} 📊  Monthly Summary")
    print(f"  {Color.CYAN}5.{Color.RESET} ✏️   Edit an Expense")
    print(f"  {Color.CYAN}6.{Color.RESET} 🗑️   Delete an Expense")
    print(f"  {Color.CYAN}7.{Color.RESET} 🚪  Exit")
    print(f"{Color.BOLD}{'─'*40}{Color.RESET}")


def main():
    """
    Entry point. Initialize storage, then run the menu loop.
    Exits cleanly on choice 7 or Ctrl+C.
    """
    initialize_csv()

    while True:
        print_banner()
        show_menu()

        choice = input(f"\n{Color.BOLD}Enter your choice (1–7): {Color.RESET}").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            filter_by_category()
        elif choice == "4":
            monthly_summary()
        elif choice == "5":
            edit_expense()
        elif choice == "6":
            delete_expense()
        elif choice == "7":
            print(f"\n{Color.GREEN}Goodbye! Stay on top of your finances. 💪{Color.RESET}\n")
            sys.exit(0)
        else:
            print(f"{Color.RED}[ERROR] Invalid choice. Enter a number from 1 to 7.{Color.RESET}")
            input("\nPress Enter to continue...")


# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}[INFO] App closed with Ctrl+C. Bye!{Color.RESET}\n")
        sys.exit(0)
