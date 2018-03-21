# *f.tea.p*

### A basic ftp client with python and PyQt5.

This application is an ftp client. It does a few basic operations.

GUI is made with [Qt](https://www.qt.io/)'s python binding [PyQt5](https://sourceforge.net/projects/pyqt/).
[ftplib](https://docs.python.org/3/library/ftplib.html) is used for ftp backend.

When you run the program with:

```
$ python fteap.py
```

You should see the login window:

![Login window.](/ss/login_screen.png?raw=true)

After you have given the credentials, main window appears:

![Main window.](ss/main_screen.png?raw=true)

As can be seen from the screenshot, available operations are:

* RETR: Fetches the selected file on the remote listing.
* STOR: Pushes selected local file from tree onto the current remote directory.
* RN: Renames selected file on the remote listing. A little line edit and button controls appear when you click this, so that you can enter the new name.
![Renaming]((ss/rename.png?raw=true)
* DELE: Deletes selected file on the remote listing.
* RMD: Removes selected directory on the remote listing.
* MKD: Makes a directory on the current remote path by the name input in the same little line edit.

You can enter the selected directory either on the tree or the list by clicking the `->` button. Likewise, you can go up one directory by clicking `^` button.

GUI design is made with Qt Designer and a good introduction guide can be found [here](http://pyqt.sourceforge.net/Docs/PyQt5/designer.html) for generating python
classes from `ui` files and using the generated code afterwards.

#### Dependencies

In order GUI to work --it doesn't work without GUI by the way ^^;--, you need Qt python binding PyQt5. On Arch Linux, you can get it from the main repo:

```
$ pacman -S python-pyqt5
```

To connect an ftp server locally, you must have an ftp daemon running as a service on your local machine. For this, you can install vsftpd. On Arch Linux, you can
install it via pacman:

```
$ pacman -S vsftpd
```
    
If you are encountering permission issues, consider changing default settings of vsftpd by editing /etc/vsftpd.conf. By default, you can connect to the server anonymously.
If you want to connect as a local user as well, you should enable it by adding `local\_enable=YES` to the configuration file mentioned above. Additionally you should add the
`write\_enable=YES` line to execute any write operation.

