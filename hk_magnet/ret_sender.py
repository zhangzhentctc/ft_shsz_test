import smtplib
from email.mime.text import MIMEText

RET_OK = 0
RET_ERR = -1
class ret_sender:
    def __init__(self, subject, content, passwd):
        self.host = 'smtp.163.com'
        self.username = 'zhangzhentctc@163.com'
        self.passwd = passwd
        self.to_list = ['aaronzhenzhang@gmail.com']
        self.subject = subject
        self.content = content

    def send_email(self):
        msg = MIMEText(self.content.encode('utf8'), _subtype='html', _charset='utf8')
        msg['From'] = self.username
        msg['Subject'] = u'%s' % self.subject
        msg['To'] = ",".join(self.to_list)

        try:
            s = smtplib.SMTP_SSL(self.host, 465)
        except:
            print('smtp init fail')
            return RET_ERR

        try:
            s.login(self.username, self.passwd)
        except:
            print('mail login fail')
            return RET_ERR

        try:
            s.sendmail(self.username, self.to_list, msg.as_string())
        except:
            print('mail send fail')
            return RET_ERR

        try:
            s.close()
        except:
            print('mail close fail')
            return RET_ERR

        return RET_OK
