import requests
import settings

def send_notification(title='Title', message='message', url=None, url_title=None):
    r = requests.post('https://api.pushover.net/1/messages.json', data={
        'token'     : settings.PUSHOVER_TOKEN,
        'user'      : settings.PUSHOVER_USER_KEY,
        'title'     : title,
        'message'   : message,
        'url'       : url,
        'url_title' : url_title,
    })
    if r.status_code != 200:
        raise Exception('Failed request with status {}'.format(r.status_code))

if __name__ == '__main__':
    send_notification(
        title='From python',
        message='hello',
        url='http://192.168.1.72',
        url_title='Go to video'
    )
