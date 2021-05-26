from ftplib import FTP, FTP_TLS
import os 

class MyFTP_TLS(FTP_TLS):
    def ntransfercmd(self, cmd, rest=None):
        conn, size = FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,server_hostname=self.host,session=self.sock.session) 
        return conn, size

class FTP_SERVER:
    ''' Setup ftp server '''
    def __init__(self, host_addr, host_port, user, psw, timeout=5):
        self.FTP_HOST = host_addr            # set ftp server address
        self.FTP_PORT = host_port            # set ftp server port
        self.FTP_USER = user                 # set ftp user
        self.FTP_PASS = psw                  # set ftp password
        self.FTP_TIMEOUT = timeout           # set ftp timeout
        self.ftps = MyFTP_TLS(timeout=self.FTP_TIMEOUT)
    
    ''' Start ftps connection '''
    def start_ftps(self):
        self.ftps.connect(self.FTP_HOST, self.FTP_PORT)
        self.ftps.auth()
        self.ftps.prot_p()
        self.ftps.login(self.FTP_USER, self.FTP_PASS) 
        # self.ftps.set_debuglevel(2)
        self.ftps.set_pasv(True)

    ''' get list of all files in ftp server '''
    def get_files(self, dir, ext):
        self.start_ftps()
        allfiles = list()
        self.ftps.cwd(dir)
        files = self.ftps.nlst()
        for f in files:
            if self.isdir(f):
                allfiles = allfiles + self.get_files(f, ext)
            elif f.endswith(ext):
                # check file extention
                allfiles.append(f)
        return allfiles

    ''' check if path is directory or file '''
    def isdir(self, name):
        try:
            self.ftps.cwd(name)
            self.ftps.cwd('..')
            return True
        except:
            return False

    ''' check if path exist on ftp server'''
    def isExist(self, file_path):
        try:
            self.ftps.get(file_path)
            return True
        except FileNotFoundError:
            return False

    ''' download file from ftp server '''
    def download_file(self, file_path):
        dirname = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        self.start_ftps()
        self.ftps.cwd(dirname)
        self.ftps.retrbinary(f"RETR {filename}", open(os.path.join(".", filename),"wb").write)
        # print("dwn:", filename)

    ''' upload file to ftp server '''
    def upload_file(self, input_file, out_path):
        self.start_ftps()
        self.ftps.cwd(out_path)
        filename = os.path.basename(input_file)
        with open(input_file, "rb") as file:
            # use FTP's STOR command to upload the file
            self.ftps.storbinary(f"STOR {filename}", file)

