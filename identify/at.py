__author__ = 'Monte'
import urllib
import urllib2
import json
import sys


class Messenger(object):
    def __init__(self, recipients, msg, sender=None):
        self.username = "CBinyenya"
        self.api_key = "9496be239c872953f0ff82006c79cdaf081d896fc087ef46954a1256ae5560f3"
        if sender:
            self.sender_id = unicode(sender)
        else:
            self.sender_id = sender
        self.recipients = recipients
        self.msg = msg

    def recipient(self):
        if isinstance(self.recipients, list):
            user2 = ""
            for user in self.recipients:
                user2 = user2 + "," + str(user)
            return user2[1:]

        if len(self.recipients) == 13:
            return self.recipients

    @staticmethod
    def get_cost(cost):
        amount = str(cost).replace("K", "").replace("E", "").replace("S", "")
        return float(amount)

    @staticmethod
    def response_handler(response):
        total_cost = 0
        success = list()
        failed = list()
        if not response:
            return [], [], 0
        for every in response:
            cost = every[-1]
            if cost > 0:
                total_cost += cost
                success.append(every)
            else:
                failed.append(every)
        return success, failed, total_cost

    def send_message(self):
        if not self.sender_id:
            gateway = AfricasTalkingGateway(self.username, self.api_key)
        else:
            gateway = AfricasTalkingGateway(self.username, self.api_key, self.sender_id)
        to = self.recipient()
        response = list()
        try:
            recipients = gateway.send_message(to, self.msg)
            for recipient in recipients:
                # Note that only the Status "Success" means the message was sent
                response.append((recipient['number'], self.msg, recipient['status'],
                                 Messenger.get_cost(recipient['cost'])))
            return Messenger.response_handler(response)
        except AfricasTalkingGatewayException, e:
            print 'Encountered an error while sending: %s' % str(e)


class AfricasTalkingGatewayException(Exception):
    pass


class AfricasTalkingGateway:
    def __init__(self, username_, apiKey_, from_=None):
        self.from_ = from_
        self.username = username_
        self.apiKey = apiKey_
        self.SMSURLString = "https://api.africastalking.com/version1/messaging"
        self.VoiceURLString = "https://voice.africastalking.com/call"

    def send_message(self, to_, message_, from_ = None, bulkSMSMode_ = 1, enqueue_ = 0, keyword_ = None, linkId_ = None):
        """
        The optional from_ parameter should be populated with the value of a shortcode or alphanumeric that is
        registered with us
        The optional bulkSMSMode_ parameter will be used by the Mobile Service Provider to determine who gets billed for a
        message sent using a Mobile-Terminated ShortCode. The default value is 1 (which means that
        you, the sender, gets charged). This parameter will be ignored for messages sent using
        alphanumerics or Mobile-Originated shortcodes.
        The optional enqueue_ parameter is useful when sending a lot of messages at once where speed is of the essence

         The optional keyword_ is used to specify which subscription product to use to send messages for premium rated short codes

         The optional linkId_ parameter is pecified when responding to an on-demand content request on a premium rated short code

        """
        if len(to_) == 0 or len(message_) == 0:
                raise AfricasTalkingGatewayException("Please provide both to_ and message_ parameters")

        values = {
            'username': self.username,
            'to': to_,
            'message': message_
        }

        from_ = self.from_
        if from_ is not None:
            values["from"] = self.from_
            values["bulkSMSMode"] = bulkSMSMode_

        if enqueue_ > 0:
            values["enqueue"] = enqueue_

        if keyword_ is not None:
            values["keyword"] = keyword_

        if linkId_ is not None:
            values["linkId"] = linkId_

        headers = {
            'Accept': 'application/json',
            'apikey': self.apiKey
        }

        try:
            data = urllib.urlencode(values)
            request = urllib2.Request(self.SMSURLString, data, headers=headers)
            response = urllib2.urlopen(request)
            the_page = response.read()
        except urllib2.HTTPError as e:
            print e
            the_page = e.read()
            decoded = json.loads(the_page)
            raise AfricasTalkingGatewayException(decoded['SMSMessageData']['Message'])
        except urllib2.URLError:
            print >>sys.stderr, "Internet connection error"
        else:
            decoded = json.loads(the_page)
            recipients = decoded['SMSMessageData']['Recipients']
            return recipients

    def fetchMessages(self, lastReceivedId_):

        url = "%s?username=%s&lastReceivedId=%s" % (self.SMSURLString, self.username, lastReceivedId_)
        headers = {
            'Accept': 'application/json',
            'apikey': self.apiKey
        }

        try:
            request = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(request)
            the_page = response.read()

        except urllib2.HTTPError as e:

            the_page = e.read()
            decoded = json.loads(the_page)
            raise AfricasTalkingGatewayException(decoded['SMSMessageData']['Message'])

        else:

            decoded = json.loads(the_page)
            messages = decoded['SMSMessageData']['Messages']

            return messages

    def call(self, from_, to_):
        values = {
            'username': self.username,
            'from': from_,
            'to': to_
        }

        headers = {
            'Accept': 'application/json',
            'apikey': self.apiKey
        }

        try:
            data = urllib.urlencode(values)
            request = urllib2.Request(self.VoiceURLString, data, headers=headers)
            response = urllib2.urlopen(request)

        except urllib2.HTTPError as e:

            the_page = e.read()
            decoded = json.loads(the_page)
            raise AfricasTalkingGatewayException(decoded['ErrorMessage'])
