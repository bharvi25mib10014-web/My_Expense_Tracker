import calendar
import datetime
import os
from typing import List, Dict, Optional # Note: 'typing' is used for clear documentation (type hints) but the logic does not rely on advanced types.

# --- Constants for Categorization and Budgeting ---
# The 5 primary categories for tracking spending.
CORE_CATEGORIES = [
    "🍔 Food",
    "🏠 Home",
    "💼 Work",
    "🎉 Fun",
    "✨ Misc",
]
# Category for the overall savings goal.
SAVINGS_CATEGORY = "💰 Savings" 
# Category for money taken out of savings (to keep a record).
SAVINGS_USE_CATEGORY = "❌ Savings_Use" 

# 1. Define the Expense Class (A simple way to represent structured data)
class Expense:
    """Represents a single expense record, including the timestamp of creation."""
    def __init__(self, name: str, category: str, amount: float, timestamp: Optional[str] = None):
        self.name = name
        self.category = category
        self.amount = amount
        # Sets the current date/time if not provided
        self.timestamp = timestamp if timestamp else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        """String representation of the Expense object for debugging/display."""
        return f"<Expense: {self.name}, {self.amount:.2f}, {self.category}, {self.timestamp}>"

# --- CORE FUNCTIONS ---

def get_user_expense(categories: List[str]) -> Expense:
    """Prompts the user for a single expense entry using basic input/output and loops."""
    print(f"\n--- Add New Expense ---")

    # Ensures name is not empty (while loop for validation)
    while True:
        expense_name = input("Enter expense name: ")
        if expense_name.strip():
            break
        print("Expense name cannot be empty. Try again!")

    # Ensures amount is positive and valid (try/except for error handling)
    while True:
        try:
            expense_amount = float(input("Enter expense amount (in ₹): "))
            if expense_amount > 0:
                break
            print("Amount must be positive.")
        except ValueError:
            print("Please enter a valid number.")
    
    # User selects category using a numbered list (for loop and conditional checks)
    while True:
        print("\nSelect a category: ")
        for i, category_name in enumerate(categories):
            print(f"  {i + 1}. {category_name}")

        value_range = f"[1 - {len(categories)}]"
        try:
            selected_index = int(input(f"Enter a category number {value_range}: ")) - 1
            if selected_index in range(len(categories)):
                selected_category = categories[selected_index]
                break
            else:
                print("Invalid category. Please try again!")
        except ValueError:
            print("Please enter a valid number.")

    new_expense = Expense(
        name=expense_name, category=selected_category, amount=expense_amount
    )
    return new_expense

def load_expenses(expense_file_path: str) -> List[Expense]:
    """Reads all expenses from the CSV file and converts them to Expense objects."""
    expenses: List[Expense] = []
    try:
        # File Handling (using try/except for error management)
        with open(expense_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue 

                parts = line.split(",") # String manipulation
                
                # Basic check for structure integrity
                if len(parts) >= 3:
                    expense_name = parts[0]
                    expense_amount_str = parts[1]
                    expense_category = parts[2]
                    timestamp = parts[3] if len(parts) >= 4 else None
                    
                    try:
                        line_expense = Expense(
                            name=expense_name,
                            amount=float(expense_amount_str),
                            category=expense_category,
                            timestamp=timestamp
                        )
                        expenses.append(line_expense) # Appending to a list
                    except ValueError:
                        print(f"Warning: Skipping malformed amount in line: {line}")
                else:
                    print(f"Warning: Skipping malformed line with too few fields: {line}")

    except FileNotFoundError:
        print(f"Info: Expense file '{expense_file_path}' not found. Creating a new one.")
        pass
    except Exception as e:
        print(f"Error loading expenses: {e}")
        
    return expenses

def save_all_expenses(expenses: List[Expense], expense_file_path: str):
    """Writes all expenses back to the file (used for saving and deletion)."""
    try:
        # 'w' mode overwrites the entire file.
        with open(expense_file_path, "w", encoding="utf-8") as f:
            for expense in expenses:
                f.write(f"{expense.name},{expense.amount:.2f},{expense.category},{expense.timestamp}\n")
    except Exception as e:
        print(f"Error saving all expenses: {e}")

def save_new_expense(expense: Expense, expense_file_path: str):
    """Appends a single new expense to the file."""
    print(f"🎯 Saving User Expense: {expense.name} to {expense_file_path}")
    
    # 'a' mode appends to the end of the file.
    try:
        with open(expense_file_path, "a", encoding="utf-8") as f:
            f.write(f"{expense.name},{expense.amount:.2f},{expense.category},{expense.timestamp}\n")
    except Exception as e:
        print(f"Error saving expense: {e}")


def delete_expense(expense_file_path: str):
    """Allows the user to select and delete an expense by index."""
    print("\n--- Delete Expense ---")
    all_expenses = load_expenses(expense_file_path)

    if not all_expenses:
        print(red("No expenses found to delete."))
        return

    print("Current Expenses:")
    # Display indexed list of expenses
    for i, exp in enumerate(all_expenses):
        print(f"  {i + 1}. {exp.timestamp[:10]} | {exp.category:<12} | ₹{exp.amount:8.2f} | {exp.name}")

    while True:
        try:
            selection = input(f"Enter the number of the expense to delete (1-{len(all_expenses)}) or 'c' to cancel: ")
            if selection.lower() == 'c':
                print("Deletion cancelled.")
                return
            
            index_to_delete = int(selection) - 1
            if 0 <= index_to_delete < len(all_expenses):
                deleted_expense = all_expenses.pop(index_to_delete) # List operation (removal)
                print(red(f"DELETED: {deleted_expense.name}"))
                
                # Rewrite the entire file with the remaining expenses
                save_all_expenses(all_expenses, expense_file_path)
                return
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'c'.")

def record_savings_use(expense_file_path: str):
    """Records an amount taken from savings for extra purchases."""
    print("\n--- Record Savings Use ---")

    while True:
        try:
            amount_used = float(input("Enter the amount you took from savings (in ₹): "))
            if amount_used > 0:
                break
            print("Amount must be positive.")
        except ValueError:
            print("Please enter a valid number.")

    reason = input("Enter a brief reason for using savings (e.g., 'Emergency Car Repair'): ")
    
    savings_use_expense = Expense(
        name=f"Used for: {reason}", 
        category=SAVINGS_USE_CATEGORY, 
        amount=amount_used
    )
    
    save_new_expense(savings_use_expense, expense_file_path)
    print(yellow(f"Recorded ₹{amount_used:.2f} used from savings for '{reason}'."))


def summarize_expenses(expense_file_path: str, category_budgets: Dict[str, float], filter_month: Optional[int] = None, filter_year: Optional[int] = None):
    """Reads, filters, and summarizes expenses, including budget breakdown and savings utilization."""
    print(f"\n--- Expense Summary 📊 ---")
    
    all_expenses = load_expenses(expense_file_path)
    filtered_expenses: List[Expense] = []
    
    # Filtering logic (using datetime for date comparisons)
    for exp in all_expenses:
        try:
            expense_date = datetime.datetime.strptime(exp.timestamp, "%Y-%m-%d %H:%M:%S")
            
            month_match = (filter_month is None) or (expense_date.month == filter_month)
            year_match = (filter_year is None) or (expense_date.year == filter_year)
            
            if month_match and year_match:
                filtered_expenses.append(exp)
        except:
            # Skip expenses with malformed timestamps
            continue 

    if filter_month and filter_year:
        print(f"Summary for: {calendar.month_name[filter_month]} {filter_year}")
    
    if not filtered_expenses:
        print(yellow("No expenses found for this period."))
        return

    # Calculate spending by category (using a dictionary)
    spending_by_category: Dict[str, float] = {cat: 0.0 for cat in category_budgets.keys()}
    total_savings_used = 0.0
    
    for expense in filtered_expenses:
        if expense.category in spending_by_category:
            spending_by_category[expense.category] += expense.amount
        elif expense.category == SAVINGS_USE_CATEGORY:
            total_savings_used += expense.amount

    total_budget = sum(category_budgets.values())
    total_spent = sum(spending_by_category.values())
    
    # Calculate days left for the Daily Limit
    now = datetime.datetime.now()
    is_current_month = (filter_month == now.month) and (filter_year == now.year)

    print("\n--- Category Breakdown vs. Budget ---")
    BAR_LENGTH = 30
    
    for category, budget_amount in category_budgets.items():
        spent_amount = spending_by_category.get(category, 0.0)
        remaining = budget_amount - spent_amount
        
        if budget_amount > 0:
            percentage_used = spent_amount / budget_amount
        else:
            percentage_used = 0 
            
        filled_length = int(BAR_LENGTH * min(percentage_used, 1.0))
        
        # Simple character-based bar chart for visualization
        if remaining >= 0:
            bar = green('█' * filled_length) + '-' * (BAR_LENGTH - filled_length)
        else:
            bar = red('█' * BAR_LENGTH) 
            
        print(f"  {category:<12} | ₹{spent_amount:8.2f}/₹{budget_amount:.2f} | {bar} {percentage_used:.1%}")

    print("\n-----------------------------")
    print(f"💰 Total Budget: ₹{total_budget:.2f}")
    print(f"💵 Total Spent:  ₹{total_spent:.2f}")

    # Savings Goal Tracking
    initial_savings_goal = category_budgets.get(SAVINGS_CATEGORY, 0)
    adjusted_savings_goal = initial_savings_goal - total_savings_used
    
    print(green(f"⭐ Initial Savings Goal: ₹{initial_savings_goal:.2f}"))
    if total_savings_used > 0:
        print(red(f"❌ Money Used from Savings: ₹{total_savings_used:.2f}"))
    print(green(f"⭐ Adjusted Savings Goal: ₹{adjusted_savings_goal:.2f}"))
    

    # Daily Spending Limit Calculation
    total_spending_budget = total_budget - initial_savings_goal
    remaining_spending_budget = total_spending_budget - total_spent
    
    print(f"\n✅ Spending Left (Excl. Savings): ₹{remaining_spending_budget:.2f}")

    if is_current_month:
        try:
            days_in_month = calendar.monthrange(now.year, now.month)[1]
        except Exception:
            days_in_month = 30 
            
        remaining_days = days_in_month - now.day + 1
        
        if remaining_days > 0:
            daily_budget = remaining_spending_budget / remaining_days
        else:
            daily_budget = remaining_spending_budget
            
        print(green(f"👉 Daily Spending Limit (Days Left: {remaining_days}): ₹{daily_budget:.2f}"))


# --- UTILITY FUNCTIONS ---
# Functions for simple ANSI color output
def green(text):
    return f"\u001B[92m{text}\u001B[0m"

def red(text):
    return f"\u001B[91m{text}\u001B[0m"

def yellow(text):
    return f"\u001B[93m{text}\u001B[0m"

def display_budgeting_tips():
    """Menu option for documentation on the budget philosophy."""
    print("\n--- Understanding Your Budget Setup ---")
    print(yellow("Goal:"))
    print("The primary goal is to prioritize your financial future.")
    print("By setting your Savings Goal first, you ensure you 'pay yourself first.'")
    
    print(yellow("\nHow the Budget is Calculated (Flexible Method):"))
    print("1. Enter your Total Money/Income (in ₹).")
    print("2. You manually set your desired '💰 Savings' amount (Your Financial Goal).")
    print("3. The remaining money is the 'Total Spending Budget.'")
    print("4. This Spending Budget is then divided equally across the 5 core spending categories (Food, Home, Work, Fun, Misc).")
    
    print(yellow("\nBudget Flexibility:"))
    print("This method gives you full control over your most important goal (Savings).")
    print("The equal split for the 5 spending categories is a starting *guideline* to prevent overspending, but you can always adjust your Savings Goal at the start of the month to account for fixed high costs (like rent).")
    print("-" * 40)


def get_total_money_and_calculate_budgets() -> Dict[str, float]:
    """Prompts for total income and calculates the 6 category budgets, allowing manual savings input."""
    print("\n--- Budget Setup ---")
    total_money = 0.0
    
    # Input validation for total money
    while True:
        try:
            total_money = float(input("Enter your total money/income for the month (in ₹): "))
            if total_money > 0:
                break
            print("Total money must be positive.")
        except ValueError:
            print("Please enter a valid number.")

    # User defines the Savings Goal first (Conditional logic)
    savings_goal = 0.0
    while True:
        try:
            # Provide a simple 20% guideline
            print(f"\nRecommended savings goal (20% of income) is: ₹{total_money * 0.2:.2f}")
            savings_goal = float(input(f"Enter your desired Savings Goal ({SAVINGS_CATEGORY}) in ₹: "))
            
            if savings_goal >= 0 and savings_goal <= total_money:
                break
            elif savings_goal > total_money:
                print(red("Savings goal cannot exceed your total money. Please enter a lower amount."))
            else:
                print("Savings goal must be non-negative.")
        except ValueError:
            print("Please enter a valid number.")

    remaining_for_spending = total_money - savings_goal
    
    # Divide remaining equally among the 5 CORE_CATEGORIES
    num_spending_categories = len(CORE_CATEGORIES)
    
    if remaining_for_spending < 0:
        print(red("\nWarning: Your spending budget is negative! Please reduce your savings goal."))
        spending_budget_per_cat = 0.0
    else:
        spending_budget_per_cat = remaining_for_spending / num_spending_categories
    
    # Building the final budget dictionary
    category_budgets = {SAVINGS_CATEGORY: savings_goal}
    for cat in CORE_CATEGORIES:
        category_budgets[cat] = spending_budget_per_cat
        
    print(green(f"\nYour Savings Goal ({SAVINGS_CATEGORY}): ₹{savings_goal:.2f}"))
    print(green(f"Total Spending Budget Remaining: ₹{remaining_for_spending:.2f}"))
    print(green(f"SPENDING BUDGET per Category (5 categories): ₹{spending_budget_per_cat:.2f}"))
    print("-" * 40)
    return category_budgets


def main():
    expense_file_path = "expenses.csv"
    
    print(f"🎯 Running Expense Tracker!")
    
    # Password Protection (simple conditional check)
    password = input("Enter password to access tracker: ")
    if password != "mytracker2025":
        print("Access denied!")
        return

    # 1. Dynamic Budget Calculation
    category_budgets = get_total_money_and_calculate_budgets()
    
    # 2. Main Menu Loop (using a while loop)
    while True:
        print("\n--- Main Menu ---")
        print("1. Add New Expense")
        print("2. View Current Summary")
        print("3. View Specific Month/Year Summary")
        print("4. Delete Expense")
        print("5. Record Savings Use") 
        print("6. Budgeting Philosophy (Documentation)") 
        print("7. Exit")
        
        choice = input("Enter choice (1-7): ")

        # Conditional branching (if/elif/else) for menu navigation
        if choice == '1':
            expense = get_user_expense(CORE_CATEGORIES)
            save_new_expense(expense, expense_file_path)
        
        elif choice == '2':
            now = datetime.datetime.now()
            summarize_expenses(expense_file_path, category_budgets, now.month, now.year)

        elif choice == '3':
            try:
                year = int(input("Enter year (e.g., 2024): "))
                month = int(input("Enter month (1-12): "))
                summarize_expenses(expense_file_path, category_budgets, month, year)
            except ValueError:
                print(red("Invalid year or month. Try again."))

        elif choice == '4':
            delete_expense(expense_file_path)

        elif choice == '5':
            record_savings_use(expense_file_path)
            
        elif choice == '6':
            display_budgeting_tips()

        elif choice == '7':
            print("Exiting Expense Tracker. Goodbye!")
            break

        else:
            print(red("Invalid choice. Please enter a number between 1 and 7."))

if __name__ == "__main__":
    main()