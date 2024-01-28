import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
import tkinter as tk
from requests_oauthlib import OAuth1Session
import webbrowser

reddit_urls_to_fetch=[]
urls_to_fetch = []


class BrowserWindow(QMainWindow):
    def __init__(self, urls):
        super().__init__()
        self.setWindowTitle("Embedded Browser")
        self.setGeometry(100, 100, 800, 600)

        self.urls = [QUrl(url) for url in urls]  # Convert strings to QUrl objects
        self.current_url_index = 0

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.central_widget.layout().addWidget(self.scroll_area)

        self.container_widget = QWidget()  # Container widget to hold all the web views
        self.container_layout = QVBoxLayout()  # Layout to add web views vertically
        self.container_widget.setLayout(self.container_layout)

        self.scroll_area.setWidget(self.container_widget)

        self.load_next_url()

    def load_next_url(self):
        if self.current_url_index < len(self.urls):
            web_view = QWebEngineView()
            web_view.setFixedWidth(900)  # Set the width of each web view
            web_view.setMinimumSize(900, 1000)  # Set the minimum size for the web view
            web_view.load(self.urls[self.current_url_index])
            web_view.loadFinished.connect(self.on_load_finished)  # Connect loadFinished signal
            self.container_layout.addWidget(web_view)

    def on_load_finished(self, ok):
        if ok:
            self.current_url_index += 1
            self.load_next_url()

def fetch_and_display_urls():
    app = QApplication(sys.argv)
    window = BrowserWindow(urls_to_fetch)
    window.show()
    sys.exit(app.exec_())
    
def display_media(data_text, data):
    for post in data['response']['posts']:
        post_url = post['post_url']
        print(post_url)
        urls_to_fetch.append(post_url)  # Append post URLs to the list
    fetch_and_display_urls()

def retrieve_home_page(tumblr_session, data_text, root):
    response = tumblr_session.get('https://api.tumblr.com/v2/user/dashboard')
    if response.status_code == 200:
        data = response.json()
        
        display_media(data_text, data)
    else:
        data_text.insert(tk.END, f"Failed to retrieve the home page. Status code: {response.status_code}\n")




def authenticate():
    def open_auth_url():
        webbrowser.open(authorization_url)

    def submit_verifier():
        verifier = verifier_entry.get()
        access_token = tumblr.fetch_access_token('https://www.tumblr.com/oauth/access_token', verifier=verifier)
        access_token_entry.delete(0, tk.END)
        access_token_entry.insert(tk.END, access_token.get('oauth_token'))
        access_token_secret_entry.delete(0, tk.END)
        access_token_secret_entry.insert(tk.END, access_token.get('oauth_token_secret'))

    def login_with_credentials():
        access_token_val = access_token_entry.get()
        access_token_secret_val = access_token_secret_entry.get()

        tumblr_session = OAuth1Session(
            client_key,
            client_secret=client_secret,
            resource_owner_key=access_token_val,
            resource_owner_secret=access_token_secret_val
        )

        retrieve_home_page(tumblr_session, data_text, root)

    client_key = 'p8hDddfp7J8qwnkze2zdQaAIJrvfMjTowiSG6kJ0BfCjfBoPSF'
    client_secret = 'SlbJRfuiskmcmUweO8qcvrRKqFocMY8lzqDCzeT6FpoAwW1fSa'

    tumblr = OAuth1Session(
        client_key,
        client_secret=client_secret,
        callback_uri='https://google.com/'
    )

    fetch_response = tumblr.fetch_request_token('https://www.tumblr.com/oauth/request_token')
    authorization_url = tumblr.authorization_url('https://www.tumblr.com/oauth/authorize')

    auth_window = tk.Toplevel(root)
    auth_window.title("Tumblr Authentication")
    auth_window.geometry("600x600") 
    frame = tk.Frame(auth_window, pady=20)  # Adding more padding to the frame
    frame.pack()
    button_style = {'font': ('Arial', 14), 'width': 25, 'height': 2}  # Increase font and button size

    auth_url_label = tk.Label(auth_window, text="Visit the URL and get the verifier:", font=("Arial", 20))
    auth_url_label.pack(pady=20)

    auth_url_button = tk.Button(frame, text="Open Authorization URL", command=open_auth_url,**button_style)
    auth_url_button.pack()

    data_text = tk.Text(root, wrap='word')  # 'word' wrapping for long lines
    data_text.pack(expand=True, fill='both')
    
    verifier_label = tk.Label(auth_window, text="Verifier:", font=("Arial", 20))
    verifier_label.pack(pady=20)

    verifier_entry = tk.Entry(auth_window,width=60)
    verifier_entry.pack(pady=20)

    scrollbar = tk.Scrollbar(root, command=data_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill='y')
    data_text.config(yscrollcommand=scrollbar.set)

    submit_verifier_button = tk.Button(frame, text="Submit Verifier", command=submit_verifier,**button_style)
    submit_verifier_button.pack()

    access_token_label = tk.Label(auth_window, text="Access Token:")
    access_token_label.pack()
    access_token_entry = tk.Entry(auth_window)
    access_token_entry.pack()

    access_token_secret_label = tk.Label(auth_window, text="Access Token Secret:")
    access_token_secret_label.pack()
    access_token_secret_entry = tk.Entry(auth_window)
    access_token_secret_entry.pack()

    login_button = tk.Button(frame, text="Login", command=login_with_credentials,**button_style)
    login_button.pack(side=tk.BOTTOM, pady=10)
    
    
    


def access_reddit_homepage(access_token):
    headers = {'Authorization': f'Bearer {access_token}', 'User-Agent': 'YourApp/1.0'}
    home_page_url = 'https://oauth.reddit.com/'
    response = requests.get(home_page_url, headers=headers)

    if response.status_code == 200:
        home_page_data = response.json()
        # Process the user's homepage data as needed
        extract_permalink(home_page_data)
    else:
        print(f"Failed to fetch homepage. Status code: {response.status_code}")
   


    
    
def extract_permalink(data):
    if 'data' in data and 'children' in data['data']:
        for post in data['data']['children']:
            if 'data' in post and 'permalink' in post['data']:
                permalink = post['data']['permalink']
                full_permalink = f"https://www.reddit.com{permalink}"  # Prepend the base URL
                reddit_urls_to_fetch.append(full_permalink)
                print(full_permalink)
        
        fetch_and_display_reddit_urls()  

def fetch_and_display_reddit_urls():
    app = QApplication(sys.argv)
    window = BrowserWindow(reddit_urls_to_fetch)
    window.show()
    sys.exit(app.exec_())        

def new_window():
    def open_reddit_authorization_url():
    # Replace with your app details and redirect URI
        client_id = '1SCq6A3Z3B6HBeY_wQkZ8w'
        redirect_uri = 'https://google.com'
        auth_url = f'https://www.reddit.com/api/v1/authorize?client_id={client_id}&response_type=code&state=random_state&redirect_uri={redirect_uri}&duration=permanent&scope=read'

        webbrowser.open_new(auth_url)
    def get_reddit_access_token():
        verifier_code = verifier_entry.get()  # Get the verifier code entered by the user

        # Replace with your app details
        client_id = '1SCq6A3Z3B6HBeY_wQkZ8w'
        client_secret = '-AeAKi0TCXcn0cbgOVJDq1_CtD_HmA'
        redirect_uri = 'https://google.com'
        token_url = 'https://www.reddit.com/api/v1/access_token'

        data = {
            'grant_type': 'authorization_code',
            'code': verifier_code,
            'redirect_uri': redirect_uri
        }

        reddit_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        response = requests.post(token_url, auth=reddit_auth, data=data)
        
        if response.status_code == 200:
            access_token = response.json()['access_token']
            # Use the access_token to fetch user's homepage or perform other API requests
            # Implement your logic here
            access_reddit_homepage(access_token)
        # print("Access Token:", access_token)
        else:
            print("Failed to retrieve access token")
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.content)

    
    auth_window = tk.Toplevel(root)
    auth_window.title("Reddit Authentication")

    auth_window.geometry("600x450") 
    frame = tk.Frame(auth_window, pady=20)  # Adding more padding to the frame
    frame.pack()

# Configure button appearance
    button_style = {'font': ('Arial', 14), 'width': 25, 'height': 2}  # Increase font and button size


    auth_url_label = tk.Label(auth_window, text="Visit the URL and get the verifier:", font=("Arial", 20))
    auth_url_label.pack(pady=20)

    auth_url_button = tk.Button(frame, text="Open Authorization URL", command=open_reddit_authorization_url,**button_style)
    auth_url_button.pack(pady=10)

    data_text = tk.Text(root, wrap='word')  # 'word' wrapping for long lines
    data_text.pack(expand=True, fill='both')
    
    verifier_label = tk.Label(auth_window, text="Verifier:", font=("Arial", 20))
    verifier_label.pack(pady=20)

   

    verifier_entry = tk.Entry(auth_window,width=60)
    verifier_entry.pack(pady=20)

    scrollbar = tk.Scrollbar(root, command=data_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill='y')
    data_text.config(yscrollcommand=scrollbar.set)

    submit_verifier_button = tk.Button(frame, text="Submit Verifier", command=get_reddit_access_token,**button_style)
    submit_verifier_button.pack(pady=10)

    



root = tk.Tk()
root.title("Logins")

# Set the root window size
root.geometry("400x250")  # Adjust the size as needed

frame = tk.Frame(root, pady=20)  # Adding more padding to the frame
frame.pack()

# Configure button appearance
button_style = {'font': ('Arial', 14), 'width': 15, 'height': 2}  # Increase font and button size

login_button = tk.Button(frame, text="Tumblr Login", command=authenticate, **button_style)
login_button.pack(pady=10)  # Adding padding around the button

reddit_login_button = tk.Button(frame, text="Reddit Login", command=new_window, **button_style)
reddit_login_button.pack()  # Packed without additional padding

root.mainloop()