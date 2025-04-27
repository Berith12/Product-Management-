from datetime import datetime
import os

def create_invoice_directories():
    """Create directories for invoices if they don't exist"""
    directories = ["Sales Invoice", "Restock Invoice"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def read_products():
    """Read products from file and return as list of dictionaries"""
    products = []
    try:
        with open("products.txt", "r") as file:
            for line in file:
                data = [x.strip() for x in line.strip().split(",")]
                if len(data) == 6:  # ID, name, brand, quantity, price, origin
                    products.append({
                        'id': int(data[0]),
                        'name': data[1],
                        'brand': data[2],
                        'quantity': int(data[3]),
                        'price': float(data[4]),
                        'origin': data[5]
                    })
        return products
    except FileNotFoundError:
        print("Products file not found!")
        return []

def save_products(products):
    """Save products list to file"""
    try:
        with open("products.txt", "w") as file:
            lines = []
            for p in products:
                line = f"{p['id']},{p['name']},{p['brand']},{p['quantity']},{p['price']},{p['origin']}"
                lines.append(line)
            file.write("\n".join(lines))
        return True
    except Exception as e:
        print(f"Error saving products: {e}")
        return False

def display_menu():
    """Display main menu"""
    print("\n" + "=" * 60 + "WeCare Product Management System" + "=" * 60)
    print("1. Display Products")
    print("2. Sell Products")
    print("3. Restock Products")
    print("4. Exit")
    print("-" * 60)

def display_products():
    """Display all products with marked up prices"""
    print("\n{:<5} {:<30} {:<20} {:<10} {:<10} {:<15}".format(
        'ID', 'Name', 'Brand', 'Quantity', 'Price (NPR)', 'Origin'))
    print("-" * 90)
    for product in read_products():
        selling_price = product['price'] * 3  # 200% markup
        print("{:<5} {:<30} {:<20} {:<10} {:<10} {:<15}".format(
            product['id'], product['name'], product['brand'], 
            product['quantity'], f"{selling_price:,.2f}", product['origin']))
    print("-" * 90)

def display_eligible_products(products, base_price):
    """Display only products that are eligible as free items"""
    print("\n=== Eligible Products for Free Selection ===")
    print("{:<5} {:<30} {:<20} {:<10} {:<10} {:<15}".format(
        'ID', 'Name', 'Brand', 'Quantity', 'Price (NPR)', 'Origin'))
    print("-" * 90)
    
    eligible_found = False
    for product in products:
        if product['price'] <= base_price and product['quantity'] > 0:
            eligible_found = True
            selling_price = product['price'] * 3  # 200% markup
            print("{:<5} {:<30} {:<20} {:<10} {:<10} {:<15}".format(
                product['id'], product['name'], product['brand'], 
                product['quantity'], f"{selling_price:,.2f}", product['origin']))
    print("-" * 90)
    
    return eligible_found

def create_purchase_invoice(supplier_name, items):
    """Generate purchase/restock invoice"""
    create_invoice_directories()
    
    invoice_no = f"RESTOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_amount = 0
    items_detail = ""
    
    for item in items:
        subtotal = item['quantity'] * item['price']
        total_amount += subtotal
        items_detail += f"""
    Product: {item['name']}
    Brand: {item['brand']}
    Quantity: {item['quantity']}
    Unit Cost (NPR): {item['price']:,.2f}
    Subtotal: NPR {subtotal:,.2f}
    {'-'*40}"""
    
    invoice = f"""
{'='*60}
                    WECARE BEAUTY
                    Purchase Invoice
{'='*60}
Invoice No: {invoice_no}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Supplier: {supplier_name}
{'-'*60}

ITEMS:{items_detail}

{'='*60}
Total Amount: NPR {total_amount:,.2f}
{'='*60}
"""
    filepath = f"Restock Invoice/{invoice_no}.txt"
    with open(filepath, "w") as file:
        file.write(invoice)
    return filepath

def create_sales_invoice(customer_name, items, free_items):
    """Generate sales invoice with buy 3 get 1 free policy"""
    create_invoice_directories()
    
    invoice_no = f"SALE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_amount = 0
    items_detail = ""
    
    for item in items:
        free_items_count = item.get('free_earned', 0)
        charged_quantity = item['quantity']
        subtotal = charged_quantity * (item['price'] * 3)  # 200% markup
        discount = item.get('discount', 0)
        total_amount += subtotal - discount
        
        items_detail += f"""
    Product: {item['name']}
    Brand: {item['brand']}
    Quantity: {item['quantity']} (including {free_items_count} free items)
    Unit Price (NPR): {item['price'] * 3:,.2f}
    Subtotal: NPR {subtotal:,.2f}
    Discount: NPR {discount:,.2f}
    {'-'*40}"""

    for free_item in free_items:
        items_detail += f"""
    Free Product: {free_item['name']}
    Brand: {free_item['brand']}
    Quantity: {free_item['quantity']}
    Unit Price (NPR): {free_item['price']:,.2f}
    {'-'*40}"""
    
    invoice = f"""
{'='*60}
                    WECARE BEAUTY
                    Sales Invoice
{'='*60}
Invoice No: {invoice_no}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Customer Name: {customer_name}
{'-'*60}

ITEMS:{items_detail}

{'='*60}
Total Amount: NPR {total_amount:,.2f}
{'='*60}

Thank you for shopping with WeCare Beauty!
Buy 3 Get 1 Free on all products!
"""
    filepath = f"Sales Invoice/{invoice_no}.txt"
    with open(filepath, "w") as file:
        file.write(invoice)
    return filepath

def sell_products():
    """Handle product sales"""
    items = []
    free_items = []
    
    # Get customer name with validation
    while True:
        customer_name = input("Enter customer name: ").strip()
        if not customer_name:
            print("Customer name cannot be empty!")
            continue
        if any(char.isdigit() for char in customer_name):
            print("Customer name should not contain numbers!")
            continue
        break
    
    products = read_products()
    if not products:
        print("No products available for sale!")
        return
    
    while True:
        try:
            display_products()
            product_id = input("\nEnter product ID: ").strip()
            
            if not product_id:
                print("Product ID cannot be empty!")
                continue
                
            try:
                product_id = int(product_id)
            except ValueError:
                print("Product ID must be a number!")
                continue
                
            product = next((p for p in products if p['id'] == product_id), None)
            if not product:
                print(f"Product with ID {product_id} not found!")
                continue
            
            quantity = input("Enter quantity: ").strip()
            if not quantity:
                print("Quantity cannot be empty!")
                continue
                
            try:
                quantity = int(quantity)
            except ValueError:
                print("Quantity must be a number!")
                continue
                
            if quantity <= 0:
                print("Quantity must be positive!")
                continue
            
            if quantity > 1000:  # Add reasonable limits
                print("Quantity exceeds maximum limit of 1000!")
                continue
                
            if product['quantity'] < quantity:
                print(f"Insufficient stock! Available: {product['quantity']}")
                continue
            
            # Add main purchase
            product['quantity'] -= quantity
            items.append({
                'name': product['name'],
                'brand': product['brand'],
                'quantity': quantity,
                'price': product['price'],
                'free_earned': quantity // 3
            })
            
            # Handle free items
            free_quantity = quantity // 3
            if free_quantity > 0:
                while True:
                    choice = input(f"\nYou've earned {free_quantity} free items! Choose an option:\n"
                                 "1. Select different products as free items\n"
                                 "2. Get discount instead\n"
                                 "Enter choice (1/2): ").strip()
                    
                    if not choice:
                        print("Choice cannot be empty!")
                        continue
                        
                    if choice not in ['1', '2']:
                        print("Invalid choice! Please enter 1 or 2.")
                        continue
                    
                    if choice == '1':
                        # Free item selection with validation
                        remaining_free = free_quantity
                        while remaining_free > 0:
                            try:
                                free_id = input(f"\nEnter product ID for free item ({remaining_free} remaining) or '0' for discount: ").strip()
                                
                                if not free_id:
                                    print("Product ID cannot be empty!")
                                    continue
                                    
                                if free_id == '0':
                                    remaining_discount = (remaining_free * product['price'] * 3) * 0.5
                                    items[-1]['discount'] = items[-1].get('discount', 0) + remaining_discount
                                    print(f"Applying discount of NPR {remaining_discount:,.2f}")
                                    break
                                
                                try:
                                    free_id = int(free_id)
                                except ValueError:
                                    print("Product ID must be a number!")
                                    continue
                                
                                free_product = next((p for p in products if p['id'] == free_id), None)
                                if not free_product:
                                    print(f"Product with ID {free_id} not found!")
                                    continue
                                
                                if free_product['price'] > product['price']:
                                    print("Selected product exceeds price limit for free items!")
                                    continue
                                
                                free_qty = input(f"Enter quantity for free item (max {remaining_free}): ").strip()
                                if not free_qty:
                                    print("Quantity cannot be empty!")
                                    continue
                                
                                try:
                                    free_qty = int(free_qty)
                                except ValueError:
                                    print("Quantity must be a number!")
                                    continue
                                
                                if free_qty <= 0 or free_qty > remaining_free:
                                    print(f"Invalid quantity! You can select up to {remaining_free} free items.")
                                    continue
                                
                                if free_qty > free_product['quantity']:
                                    print(f"Insufficient stock for free item! Available: {free_product['quantity']}")
                                    continue
                                
                                free_product['quantity'] -= free_qty
                                free_items.append({
                                    'name': free_product['name'],
                                    'brand': free_product['brand'],
                                    'quantity': free_qty,
                                    'price': free_product['price']
                                })
                                remaining_free -= free_qty
                                
                            except Exception as e:
                                print(f"An error occurred: {str(e)}")
                                continue
                        
                    elif choice == '2':
                        discount = (free_quantity * product['price'] * 3) * 0.5
                        items[-1]['discount'] = discount
                        break
            
            # Ask for more purchases
            while True:
                more = input("\nWould you like to purchase more items? (yes/no): ").strip().lower()
                if not more:
                    print("Input cannot be empty!")
                    continue
                if more not in ['yes', 'no']:
                    print("Please enter 'yes' or 'no'")
                    continue
                break
            
            if more == 'no':
                break
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.")
            continue
    
    if items:
        try:
            save_products(products)
            filepath = create_sales_invoice(customer_name, items, free_items)
            print(f"\n✓ Sales invoice created successfully: {filepath}")
        except Exception as e:
            print(f"Error saving transaction: {str(e)}")

def restock_products():
    """Handle product restocking"""
    items = []
    
    # Get supplier name with validation
    while True:
        supplier_name = input("Enter supplier name: ").strip()
        if not supplier_name:
            print("Supplier name cannot be empty!")
            continue
        if any(char.isdigit() for char in supplier_name):
            print("Supplier name should not contain numbers!")
            continue
        break

    products = read_products()
    if not products:
        print("No products database found!")
        return
        
    next_id = max((p['id'] for p in products), default=0) + 1

    while True:
        restock_choice = input("\nDo you want to restock an existing item? (yes/no): ").strip().lower()
        if not restock_choice:
            print("Choice cannot be empty!")
            continue
        if restock_choice not in ['yes', 'no']:
            print("Please enter 'yes' or 'no'")
            continue
        break

    if restock_choice == 'yes':
        while True:
            try:
                display_products()
                product_id = input("\nEnter product ID: ").strip()
                
                if not product_id:
                    print("Product ID cannot be empty!")
                    continue
                    
                try:
                    product_id = int(product_id)
                except ValueError:
                    print("Product ID must be a number!")
                    continue
                
                product = next((p for p in products if p['id'] == product_id), None)
                if not product:
                    print(f"Product with ID {product_id} not found!")
                    retry = input("Would you like to try another ID? (yes/no): ").lower()
                    if retry != 'yes':
                        break
                    continue
                
                print(f"Current stock for {product['name']}: {product['quantity']}")
                
                quantity = input("Enter quantity to restock: ").strip()
                if not quantity:
                    print("Quantity cannot be empty!")
                    continue
                    
                try:
                    quantity = int(quantity)
                except ValueError:
                    print("Quantity must be a number!")
                    continue
                
                if quantity <= 0:
                    print("Quantity must be positive!")
                    continue
                
                if quantity > 10000:  # Reasonable upper limit
                    print("Quantity exceeds maximum limit of 10,000!")
                    continue
                    
                product['quantity'] += quantity
                items.append({
                    'name': product['name'],
                    'brand': product['brand'],
                    'quantity': quantity,
                    'price': product['price']
                })
                
                while True:
                    more = input("\nWould you like to restock more existing items? (yes/no): ").strip().lower()
                    if not more:
                        print("Choice cannot be empty!")
                        continue
                    if more not in ['yes', 'no']:
                        print("Please enter 'yes' or 'no'")
                        continue
                    break
                
                if more == 'no':
                    break
                    
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again.")
                continue
    else:
        while True:
            add_new = input("\nDo you want to add new products? (yes/no): ").strip().lower()
            if not add_new:
                print("Choice cannot be empty!")
                continue
            if add_new not in ['yes', 'no']:
                print("Please enter 'yes' or 'no'")
                continue
            break

        if add_new == 'yes':
            while True:
                try:
                    name = input("\nEnter product name: ").strip()
                    if not name:
                        print("Product name cannot be empty!")
                        continue
                        
                    brand = input("Enter brand: ").strip()
                    if not brand:
                        print("Brand cannot be empty!")
                        continue
                    
                    quantity = input("Enter quantity: ").strip()
                    if not quantity:
                        print("Quantity cannot be empty!")
                        continue
                    try:
                        quantity = int(quantity)
                        if quantity <= 0:
                            print("Quantity must be positive!")
                            continue
                        if quantity > 10000:
                            print("Quantity exceeds maximum limit of 10,000!")
                            continue
                    except ValueError:
                        print("Quantity must be a number!")
                        continue
                    
                    price = input("Enter cost price: ").strip()
                    if not price:
                        print("Price cannot be empty!")
                        continue
                    try:
                        price = float(price)
                        if price <= 0:
                            print("Price must be positive!")
                            continue
                        if price > 1000000:
                            print("Price exceeds maximum limit of 1,000,000!")
                            continue
                    except ValueError:
                        print("Price must be a number!")
                        continue
                    
                    origin = input("Enter origin country: ").strip()
                    if not origin:
                        print("Origin cannot be empty!")
                        continue
                    if any(char.isdigit() for char in origin):
                        print("Origin should not contain numbers!")
                        continue
                    
                    products.append({
                        'id': next_id,
                        'name': name,
                        'brand': brand,
                        'quantity': quantity,
                        'price': price,
                        'origin': origin
                    })
                    
                    items.append({
                        'name': name,
                        'brand': brand,
                        'quantity': quantity,
                        'price': price
                    })
                    
                    next_id += 1
                    
                    while True:
                        more = input("\nWould you like to add more new products? (yes/no): ").strip().lower()
                        if not more:
                            print("Choice cannot be empty!")
                            continue
                        if more not in ['yes', 'no']:
                            print("Please enter 'yes' or 'no'")
                            continue
                        break
                    
                    if more == 'no':
                        break
                        
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    print("Please try again.")
                    continue
    
    if items:
        try:
            save_products(products)
            filepath = create_purchase_invoice(supplier_name, items)
            print(f"\n✓ Restock invoice created successfully: {filepath}")
        except Exception as e:
            print(f"Error saving transaction: {str(e)}")

def main():
    """Main program loop"""
    while True:
        try:
            display_menu()
            choice = int(input("Enter your choice: "))
            
            if choice == 1:
                display_products()
            elif choice == 2:
                sell_products()
            elif choice == 3:
                restock_products()
            elif choice == 4:
                print("Thank you for using WeCare Product Management System!")
                break
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()