import sqlite3

conn = sqlite3.connect('mini_pro.db')

c = conn.cursor()

# c.execute('''CREATE TABLE candidates_list(serial_no INT NOT NULL,candidate_name CHAR NOT NULL,pincode INT NOT NULL,image BLOB NOT NULL)''')

# c.execute("INSERT INTO candidates_list VALUES(1,'Michael Scott',560062,'D:\\Mini_project_2021\\candidate_ids\\MichaelScott.PNG')")
# c.execute("INSERT INTO candidates_list VALUES(2,'Pam Beesly',560062,'D:\\Mini_project_2021\\candidate_ids\\Pam.png')")
# c.execute("INSERT INTO candidates_list VALUES(3,'Jim Halpert',560061,'D:\\Mini_project_2021\\candidate_ids\\JimHalpert.png')")
# c.execute("INSERT INTO candidates_list VALUES(4,'Dwight Shrute',560063,'D:\\Mini_project_2021\\candidate_ids\\Dwight.png')")
# c.execute("INSERT INTO candidates_list VALUES(5,'Creed Bratton',560062,'D:\\Mini_project_2021\\candidate_ids\\Creed.png')")
#c.execute("INSERT INTO candidates_list VALUES(6,'Oscar Nunez',560063,'D:\\Mini_project_2021\\candidate_ids\\Oscar Nunez.png')")
#c.execute('''CREATE TABLE remote_ledger_copy(Previous_hash CHAR NOT NULL,Current_Hash CHAR NOT NULL,Voter_PB CHAR NOT NULL,Miner_PB CHAR NOT NULL)''')
# c.execute("SELECT * FROM remote_ledger_copy")
# c.execute("SELECT * FROM candidates_list")
# print(c.fetchall())
conn.commit()
c.execute("SELECT * FROM candidates_list")
#c.execute('''Drop TABLE candidates_list''')
print(c.fetchall())
conn.commit()


