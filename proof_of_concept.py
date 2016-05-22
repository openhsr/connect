from smb.SMBConnection import SMBConnection

userID = ''
password = ''

server_ip = '152.96.90.26'

conn = SMBConnection(userID, password, 'connect', '', domain="HSR", use_ntlm_v2=False)
assert conn.connect(server_ip, 445)
for sf in conn.listPath('skripte', '/'):
    print('Filename: %s, isDirectory: %s, filesize: %s, last_write_time: %s' %
          (sf.filename, sf.isDirectory, sf.file_size, sf.last_write_time))

conn.close()
