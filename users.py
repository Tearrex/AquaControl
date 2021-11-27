from tracker import sql_query
import bcrypt, random

# If you change the pepper, existing users will need a new password!
pepper = "hnAC!@cTr@83zfQNZt%2Yn7^jX8&Fj8pQg%HHfaX#gf&8vAmZe2!R@Rt3qLr%@p$dv%v4iPP3N1B__B4S#FaacXtEq7SdJx8dthrGtQM&Mq*uR&%au2HCLT75BSi737E9D%28ybcHr6gT!!!$"
def hash_password(plain_pass):
    salt = bcrypt.gensalt(15)
    return (bcrypt.hashpw(str(plain_pass + pepper).encode('utf-8'), salt), salt)

def validate_password(plain_pass, hashed_pass):
    return bcrypt.checkpw(str(plain_pass + pepper).encode('utf-8'), hashed_pass)

def register_user(username, password, salt):
    params = (random.randint(10000,99999), username, password, salt)
    sql_query(f"INSERT INTO users VALUES (?, ?, ?, ?)", False, True, params, 'users.db')
    print("User registered!")

if __name__ == '__main__':
    test = input("Login? (Y/n)")
    if test == "Y":
        # check user
        user = sql_query("SELECT * FROM users", True, False, None, 'users.db')[1]
        checkpass = input("Password: ")
        print(validate_password(checkpass, user[1]))
    else:
        # make user
        user = input("Username: ")
        password = input("Password: ")
        password = hash_password(password)
        salt = password[1]
        register_user(user, password[0], salt)