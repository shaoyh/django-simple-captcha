from django.db import models
from captcha.conf import settings as captcha_settings
import datetime, unicodedata, random

try:
    import hashlib # sha for Python 2.5+
except ImportError:
    import sha # sha for Python 2.4 (deprecated in Python 2.6)
    hashlib = False

class CaptchaStore(models.Model):
    challenge = models.CharField(blank=False, max_length=32)
    response = models.CharField(blank=False, max_length=32)
    hashkey = models.CharField(blank=False, max_length=40,unique=True)
    expiration = models.DateTimeField(blank=False)
    
    def save(self,*args,**kwargs):
        self.response = self.response.lower()
        if not self.expiration:
            self.expiration = datetime.datetime.now() + datetime.timedelta(minutes= int(captcha_settings.CAPTCHA_TIMEOUT))
        if not self.hashkey:
            key_ = unicodedata.normalize('NFKD', str(random.random()) + unicode(self.challenge)).encode('ascii', 'ignore') + unicodedata.normalize('NFKD', unicode(self.response)).encode('ascii', 'ignore')
            if hashlib:
                self.hashkey = hashlib.new('sha', key_).hexdigest()
            else:
                self.hashkey = sha.new(key_).hexdigest()
            del(key_)
        super(CaptchaStore,self).save(*args,**kwargs)

    def __unicode__(self):
        return self.challenge

    
    def remove_expired(cls):
        cls.objects.filter(expiration__lte=datetime.datetime.now()).delete()
    remove_expired = classmethod(remove_expired)
    