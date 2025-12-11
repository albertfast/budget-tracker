import sys
import os
from datetime import datetime, timedelta
import random
import bcrypt

# Hack for passlib + bcrypt > 4.0 compatibility
if not hasattr(bcrypt, '__about__'):
    try:
        class About:
            __version__ = bcrypt.__version__
        bcrypt.__about__ = About()
    except Exception:
        pass

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.database import User, BankAccount, Transaction, Base
from app.core.security import get_password_hash

def seed_data():
    # Create tables if they don't exist
    print("Checking/Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Starting data seeding...")

        # 1. Create Demo User
        demo_email = "albertfast@gmail.com" # Using the username from the user's curl command/screenshot
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            print(f"Creating user: {demo_email}")
            user = User(
                email=demo_email,
                password_hash=get_password_hash("abc123"), # Using password from user's context
                first_name="Albert",
                last_name="Fast",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"User {demo_email} already exists. Updating password...")
            user.password_hash = get_password_hash("abc123")
            user.is_active = True
            db.commit()
            db.refresh(user)
            print(f"Password updated for {demo_email}")

        # 2. Create Bank Account
        account_name = "Chase Checking"
        account = db.query(BankAccount).filter(
            BankAccount.user_id == user.id,
            BankAccount.account_name == account_name
        ).first()

        if not account:
            print(f"Creating bank account: {account_name}")
            account = BankAccount(
                user_id=user.id,
                plaid_access_token="access-sandbox-de3c920c-dc8d-4376-9039-3a9b52e05602", # Mock token (must start with access-sandbox)
                plaid_item_id="item-sandbox-12345",
                plaid_account_id="acc-sandbox-67890",
                account_name=account_name,
                bank_name="Chase Bank",
                account_type="depository",
                account_subtype="checking",
                mask="1234",
                current_balance=5400.50,
                available_balance=5350.00,
                is_active=True,
                last_synced_at=datetime.utcnow()
            )
            db.add(account)
            db.commit()
            db.refresh(account)
        else:
            print(f"Bank account {account_name} already exists.")

        # 3. Create Transactions
        print("Creating transactions...")
        
        # Sample categories
        categories = [
            "Food and Drink", "Groceries", "Transportation", "Housing", 
            "Entertainment", "Shopping", "Income", "Utilities"
        ]
        
        # Generate transactions for the last 30 days
        today = datetime.utcnow()
        
        # Check if we already have transactions to avoid duplicates
        existing_tx_count = db.query(Transaction).filter(Transaction.bank_account_id == account.id).count()
        
        if existing_tx_count < 10: # Only seed if few transactions exist
            transactions = []
            
            # Add some income
            transactions.append(Transaction(
                bank_account_id=account.id,
                plaid_transaction_id=f"tx-income-{random.randint(1000, 9999)}",
                amount=2500.00, # Positive for income in our model? Let's assume standard accounting: credit is positive? 
                                # Wait, usually expense apps treat expense as positive or negative depending on convention.
                                # Model says: "Positive for credits, negative for debits" (line 67)
                                # So Income = Positive, Expense = Negative.
                date=(today - timedelta(days=15)),
                description="Direct Deposit Employer",
                merchant_name="Employer Inc",
                category_primary="Income",
                category_detailed="Wages",
                is_pending=False
            ))
            
            transactions.append(Transaction(
                bank_account_id=account.id,
                plaid_transaction_id=f"tx-income-{random.randint(1000, 9999)}",
                amount=2500.00,
                date=(today - timedelta(days=1)),
                description="Direct Deposit Employer",
                merchant_name="Employer Inc",
                category_primary="Income",
                category_detailed="Wages",
                is_pending=False
            ))

            # Add expenses
            for i in range(20):
                cat = random.choice(categories)
                if cat == "Income": continue
                
                amount = round(random.uniform(10.0, 150.0), 2)
                if cat == "Housing": amount = 1200.00
                
                # Expense should be negative based on "Positive for credits, negative for debits"
                amount = -amount
                
                day_offset = random.randint(0, 30)
                tx_date = (today - timedelta(days=day_offset))
                
                transactions.append(Transaction(
                    bank_account_id=account.id,
                    plaid_transaction_id=f"tx-{i}-{random.randint(10000, 99999)}",
                    amount=amount,
                    date=tx_date,
                    description=f"Purchase at {cat} Store",
                    merchant_name=f"{cat} Store",
                    category_primary=cat,
                    category_detailed=cat,
                    is_pending=False
                ))
            
            db.add_all(transactions)
            db.commit()
            print(f"Added {len(transactions)} transactions.")
        else:
            print("Transactions already exist, skipping.")

        print("Data seeding completed successfully!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
