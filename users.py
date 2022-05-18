from tracker import sql_query
import random, platform, os
try: import bcrypt
except Exception:
    print("You are missing the bcrypt module. Try creating a virtual environment.")
    input()
    exit()

# If you change the pepper, existing users will need a new password!
PEPPER = "AddYourSpicyPepper"
def hash_password(plain_pass):
    salt = bcrypt.gensalt(15)
    return (bcrypt.hashpw(str(plain_pass + PEPPER).encode('utf-8'), salt), salt)

def validate_password(plain_pass, hashed_pass):
    return bcrypt.checkpw(str(plain_pass + PEPPER).encode('utf-8'), hashed_pass)

def register_user(username, password, salt):
    params = (random.randint(10000,99999), username, password, salt)
    sql_query(f"INSERT INTO users VALUES (?, ?, ?, ?)", False, True, params, 'users.db')
    print("User registered, try logging in with these credentials!\n")

if __name__ == '__main__':
    if not os.path.exists("users.db"):
        with open("users.db", "w") as db:
            db.write("")
        print("Created empty user database file")
    sql_query(f"""
CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL, password TEXT NOT NULL, salt TEXT DEFAULT '')
    """, False, True, None, 'users.db')
    while True:
            test = input(
                "[1] Validate User\n[2] Register User\n[3] Delete User\n[4] Exit\n")
        if test == "1":
            # check user
            _username = input("Enter username: ").lower()
                if _username.strip() == "":
                    continue
                user = sql_query(
                    "SELECT * FROM users WHERE username = (?)", True, False, (_username,), 'users.db')
            if not user:
                print("User does not exist!\n")
                continue
            else:
                _password = input(f"Enter password for {user[0][1]}: ")
                    if _password.strip() == "":
                        continue
                    if validate_password(_password, user[0][2]):
                        print("User validated!\n")
                    else:
                        print("Password is incorrect!\n")
        elif test == "2":
            # make user
            _username = input("Create username: ").lower()
                if _username.strip() == "":
                    continue
                user = sql_query(
                    "SELECT * FROM users WHERE username = (?)", True, False, (_username,), 'users.db')
            if user:
                print("Username taken!\n")
                continue
            _password = input(f"Create password for {_username}: ")
                if _password.strip() == "":
                    continue
                print("Hashing password...")
            password = hash_password(_password)
            salt = password[1]
            register_user(_username, password[0], salt)
        elif test == "3":
                users = sql_query("SELECT * FROM users",
                                  True, False, None, 'users.db')
            if not users:
                print("No users created!\n")
                continue
            usernames = [f[1] for f in users]
            print("\nUsers:")
            print("\n".join(usernames))
            while True:
                    _user = input(
                        "Type name of user to remove (or * for all): ").lower()
                    if _user.strip() == "":
                        break
                elif _user in usernames:
                        sql_query("DELETE FROM users WHERE username = (?)",
                                  False, True, (_user,), 'users.db')
                    _os = platform.system()
                        if _os == "Linux":
                            os.system("clear")
                        elif _os == "Windows":
                            os.system("cls")
                    print(f"User '{_user}' was deleted!")
                    break
                elif _user == "*":
                    prompt = input("Delete all users? (Y/n) ")
                    if prompt == "Y":
                            sql_query("DELETE FROM users", False,
                                      True, None, 'users.db')
                        print("All users have been deleted!")
                        break
                        elif prompt == "n":
                            break
                        else:
                            continue
            elif test == "4":
                break
