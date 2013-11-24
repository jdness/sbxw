from django.db import models

# Create your models here.
class Host(models.Model):
    ip = models.GenericIPAddressField()
    mac = models.CharField(max_length=48, null=True)
    hostname = models.CharField(max_length=255, null=True)

class Webrequest(models.Model):
    host = models.ForeignKey(Host)
    server = models.CharField(max_length=255)
    port = models.IntegerField()
    url = models.CharField(max_length=2048)
    t = models.DateTimeField(auto_now=True)
    istitle = models.BooleanField(default=False)
    isimage = models.BooleanField(default=False)
    issearch = models.BooleanField(default=False)
    
    def adrequest(self):
        if (self.server == "ad.doubleclick.net" or self.server == "us-u.openx.net" or 
            self.server == "mf.sitescout.com" or self.server == "ads.adsonar.com" or
            self.server == "view.atdmt.com" or self.server == "imp.bid.ace.advertising.com" or
            self.server == "platform.twitter.com" or self.server == "rad.msn.com" or
            self.server == "web.adblade.com" or self.server == "ct1.addthis.com" or
            self.server == "googleads.g.doubleclick.net" or self.server == "aax-us-west.amazon-adsystem.com" or
            self.server == "aax-us-east.amazon-adsystem.com"):
            return True
        else:
            return False
        

class Webimage(models.Model):
    webrequest = models.ForeignKey(Webrequest)
    sourcerequest = models.ForeignKey(Webrequest, related_name='images', null=True)
    md5 = models.CharField(max_length=48, null=True)
    filename = models.CharField(max_length=255, null=True)
    thumbnailfilename = models.CharField(max_length=255, null=True)
    tone = models.FloatField(null=True)
    height = models.IntegerField()
    width = models.IntegerField()
    nudity = models.NullBooleanField()
    nudity_confidence = models.IntegerField(null=True)

    def bigenough(self):
        if self.height >= 150 and self.width >= 150:
            return True
        else:
            return False
    
class Webtitle(models.Model):
    webrequest = models.OneToOneField(Webrequest, related_name='title')
    title = models.CharField(max_length=2048)
    

class Websearch(models.Model):
    webrequest = models.OneToOneField(Webrequest, related_name='websearch')
    query = models.CharField(max_length=2048)
    
    
