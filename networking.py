# 1. find IP addr on linux and mac via: nmap -sn 192.168.4.0/24
# 2. setup ssh key via:
# 2.1 create a key (local), no passphrase: ssh-keygen -t rsa
# 2.2 get the key: cat /home/.ssh/id_rsa.pub
# 2.3 copy the key to remote device: ssh-copy-id sshd@IP


import paramiko
import os
import shutil
import numpy as np


IMAGE_PREFIXES = ['jpg', 'jpeg', 'png']


class RemoteNavigator:
    """ Class for navigating on a remote server.
    """

    def __init__(self, ip: str, tmp_path: str):
        """ Init.
        :param ip: the ip addr as a str
        :param tmp_path: path to the tmp folder for cache
        """
        self.file_list_path = 'file_list.txt'
        self.ip = ip
        self.tmp_path = tmp_path
        self.con = paramiko.SSHClient()
        self.current_dir = ''
        self.rsync_lock = False

    def connect(self):
        self.con.load_system_host_keys()
        self.con.connect(self.ip, username='sshd')

    def list(self, include_folders=True, include_files=True):
        ls_cmd = ' ;ls'
        if not include_files:
            ls_cmd = ' ;ls -d */'
        elif not include_folders:
            ls_cmd = ' ;ls -p | grep -v /'
        stdin, stdout, stderr = self.con.exec_command('cd ' + self.current_dir + ls_cmd)
        output = self._process_output(stdout, stderr)
        return output

    def filter_list(self, file_list):
        filtered_list = []
        if len(file_list) <= 0:
            return filtered_list
        return list(filter(lambda k: any(pre in k for pre in IMAGE_PREFIXES), file_list))

    def goto(self, path: str):
        target_path = self.current_dir + '/' + path if len(self.current_dir) > 0 else path
        stdin, stdout, stderr = self.con.exec_command('cd ' + target_path + ' ;pwd')
        output = self._process_output(stdout, stderr)
        print(output)
        self.current_dir = output[0]
        return output

    def chunk(self, chunk_size=8, filter_list=True):
        data = self.list(include_folders=False)
        if filter_list:
            data = self.filter_list(data)
        if len(data) <= 0:
            return []
        data = np.array(data, np.str)
        n_padding = chunk_size - data.shape[0]
        if data.shape[0] > chunk_size and data.shape[0] % chunk_size != 0:
            n_padding = chunk_size - data.shape[0] % chunk_size
        n_chunks = data.shape[0] // chunk_size
        n_chunks += 1 if n_padding != 0 else 0
        if n_padding != 0:
            padding = np.full(n_padding, '')
            data = np.concatenate((data, padding), axis=0)
        data = np.reshape(data, [n_chunks, chunk_size])
        return data

    def update_file_list(self, chunk: np.array, idx: int):
        with open(self.file_list_path, 'w+') as f:
            for item in chunk[idx]:
                f.write(item + '\n')

    def files_exist(self, use_filter=True, use_file_list=True):
        tmp_files = os.listdir(self.tmp_path)
        if len(tmp_files) <= 0:
            return False
        if use_file_list:
            with open(self.file_list_path, 'r') as f:
                file_list_files = f.readlines()
                file_list_files = [s.replace('\n', '') for s in file_list_files]
                return all(t in file_list_files for t in tmp_files)
        remote_files = self.list(include_folders=False)
        if use_filter:
            remote_files = self.filter_list(remote_files)
        return all(t in remote_files for t in tmp_files)

    def download(self, clear_cache=True, use_file_list=True, enforce_update=False):
        """ Download all files in the current dir.
        """
        # if self.rsync_lock:
        #     return
        # self.rsync_lock = True
        if not enforce_update and self.files_exist():
            return
        if clear_cache:
            self.clear_cache()
        rsync_source = 'sshd@' + self.ip + ':' + self.current_dir + '/'
        if use_file_list:
            rsync_options = '--files-from=' + self.file_list_path + ' '
        else:
            rsync_includes = ' --include="*.jpg" --include="*.JPG" --include="*.jpeg" --include="*.png" '
            rsync_excludes = ' --exclude="*/" --exclude="*" '
            rsync_options = rsync_includes + rsync_excludes
        rsync_target = ' ' + self.tmp_path
        rsync_cmd = 'rsync -zaP -e ssh ' + rsync_options + rsync_source + rsync_target
        os.system(rsync_cmd)
        # self.rsync_lock = False

    def clear_cache(self):
        shutil.rmtree(self.tmp_path)
        os.makedirs(self.tmp_path)

    @staticmethod
    def _process_output(stdout, stderr):
        if stderr.read() == b'':
            processed_output = [line.strip() for line in stdout.readlines()]
        else:
            processed_output = stderr.read()
        return processed_output

    def check_connection(self):
        """ This will check if the connection is still availlable.
        Return (bool) : True if it's still alive, False otherwise.
        """
        try:
            self.con.exec_command('ls', timeout=5)
            return True
        except Exception as e:
            print("Connection lost : " + str(e))
            return False


# n = RemoteNavigator('192.168.178.39', 'tmp/')
# n.connect()
# r = n.goto('test')
# print(r)
# r = n.list()
# print(r)
# n.download()
# print('done')