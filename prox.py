#!/usr/bin/env python

from libmproxy import controller, proxy
import os, glob, sys
import Image, cStringIO
import hashlib
import os, glob, sys
import zlib
import sqlite3
import urllib
import re 
import datetime

thumbnailsize = 128, 128
staticpath = "ui//static//"

def get_skin_ratio(im):
    if im.mode is 'L':
    	return 0

    if im.format is not 'JPG' and im.format is not 'JPEG':
    	return 0

    try:
    	im = im.crop((int(im.size[0]*0.2), int(im.size[1]*0.2), im.size[0]-int(im.size[0]*0.2), im.size[1]-int(im.size[1]*0.2)))
    except (AttributeError, IOError):
    	return 0

    skin = sum([count for count, rgb in im.getcolors(im.size[0]*im.size[1]) if rgb[0]>60 and rgb[1]<(rgb[0]*0.85) and rgb[2]<(rgb[0]*0.7) and rgb[1]>(rgb[0]*0.4) and rgb[2]>(rgb[0]*0.2)])
    return float(skin)/float(im.size[0]*im.size[1])

class SbxMaster(controller.Master):
    def __init__(self,server):
    	controller.Master.__init__(self,server)


    def run(self):
    	try:
    		return controller.Master.run(self)
    	except KeyboardInterrupt:
    		self.shutdown()
	
    #	def handle_request(self,msg):
    #		hid = (msg.host,msg.port)		
    #		#print "REQUEST-> {0}://{1}{2}".format(msg.scheme,msg.host,msg.path)
    #		msg.reply()

    def handle_response(self,msg):
        hid = (msg.request.host, msg.request.port)
        msg.reply()

        if (msg.headers["Content-Type"]) and ("image/jpeg" in msg.headers["Content-Type"][0]):
            if msg.content:
                print "[IMG] -> {0}://{1}{2} ".format(msg.request.scheme,msg.request.host,msg.request.path)		
                                    
                s = cStringIO.StringIO(msg.content)
                try:
                    img = Image.open(s)
                except IOError:
                    # [IMG] -> https://pbs.twimg.com/media/BYGYoHUCEAAWxrj.jpg:large 
                    # File "/Library/Python/2.7/site-packages/PIL/Image.py", line 1980, in open
                    #  raise IOError("cannot identify image file")
                    return;
		
                # Only handling JPEGs for now
                if img.format is 'JPG' or img.format is 'JPEG':
                    height, width = img.size
                    skin_percent = get_skin_ratio(img) * 100
                    hex = hashlib.md5(img.tostring()).hexdigest()
                    filename = "{0:2.0f}_{1}.jpg".format(skin_percent,hex)
                    print "  {0}: Dim: ({1},{2}) Tone {3:2.2f} ".format(filename,height,width,skin_percent)
                    img.save(staticpath + filename)		

                    img.thumbnail(thumbnailsize, Image.ANTIALIAS)
                    thumbnailfilename = filename + ".thumbnail.jpg"
                    img.save(staticpath + thumbnailfilename, "JPEG")

                    #conn = sqlite3.connect('sbx.db')
                    conn = sqlite3.connect('db.sqlite3')
                    conn.text_factory = str
                    c = conn.cursor()
                    
                    # try to find the page from which img came by looking up referer
                    
                    if (msg.request.headers["Referer"]):
                        c.execute("SELECT id from ui_webrequest where url = ? order by id desc limit 1",msg.request.headers["Referer"])
                        data = c.fetchone()
                        if (data and data[0]):
                            referer_id = data[0]
                            print "Referrer: {0}. Fetched: {1}".format(msg.request.headers["Referer"][0],referer_id)
                        else:
                            referer_id = False
                    else:
                        referer_id = False
                    
                    url = "{0}://{1}{2}".format(msg.request.scheme,msg.request.host,msg.request.path)
                    row = (1, msg.request.host, msg.request.client_conn.address[1], url, datetime.datetime.now())		
                    c.execute("INSERT INTO ui_webrequest (host_id,server,port,url,t,istitle,isimage,issearch) VALUES (?,?,?,?,?,0,1,0); ",row)
                    conn.commit()
                    print "Inserted request #{0}.".format(c.lastrowid)

                    if (referer_id):
                        row = (c.lastrowid,referer_id,hex,filename,thumbnailfilename,skin_percent,height,width)
                        c.execute("INSERT INTO ui_webimage (webrequest_id,sourcerequest_id,md5,filename,thumbnailfilename,tone,height,width) values (?,?,?,?,?,?,?,?)",row)
                    else:
                        row = (c.lastrowid,hex,filename,thumbnailfilename,skin_percent,height,width)
                        c.execute("INSERT INTO ui_webimage (webrequest_id,md5,filename,thumbnailfilename,tone,height,width) values (?,?,?,?,?,?,?)",row)
                    conn.commit()
                    print "Inserted image #{0}.".format(c.lastrowid)

                    conn.close()
			
        elif (msg.headers["Content-Type"]) and (("text/html" in msg.headers["Content-Type"][0]) or 
                            ("application/json" in msg.headers["Content-Type"][0])):
            print "[{0}] -> {1}://{2}{3}".format(msg.code,msg.request.scheme,msg.request.host,msg.request.path)

#            conn = sqlite3.connect('sbx.db')
            conn = sqlite3.connect('db.sqlite3')
            conn.text_factory = str
            c = conn.cursor()
            url = "{0}://{1}{2}".format(msg.request.scheme,msg.request.host,msg.request.path)
            row = (1, msg.request.host, msg.request.client_conn.address[1], url, datetime.datetime.now())		
            c.execute("INSERT INTO ui_webrequest (host_id,server,port,url,t,istitle,isimage,issearch) VALUES (?,?,?,?,?,0,0,0); ",row)
            conn.commit()
            print "Inserted webrequest #{0}.".format(c.lastrowid)

            if (msg.code < 300):				
                content = msg.content
                if (msg.headers["Content-Encoding"]) and ("gzip" in msg.headers["Content-Encoding"][0]):
                    try:
                        content=zlib.decompress(msg.content, 16+zlib.MAX_WBITS)
                    except:
                        # Should really do something better here.
                        content = '<title>Failed webpage load due to zlib error.</title>'
		
                if (len(content.split('<title>')) > 1):
                    if (len(content.split('<title>')[1].split('</title>')) > 0):
                        title = content.split('<title>')[1].split('</title>')[0].strip()
                        if len(title) > 0:
                            print "Page title: [{0}]".format(title)

                            lastrowid = c.lastrowid
                            
                            row = (True,lastrowid)
                            c.execute("UPDATE ui_webrequest set istitle = ? where id = ?;",row)
                            
                            row = (lastrowid,title)
                            c.execute("INSERT INTO ui_webtitle (webrequest_id,title) values (?,?)",row)
                            conn.commit()
                            print "Inserted webpage #{0}.".format(lastrowid)
					
                if (msg.request.host == "www.google.com"):
                    if ("/search=" in msg.request.path) or ("&search=" in msg.request.path) or \
                        ("/#q=" in msg.request.path) or ("/search?" in msg.request.path):
                        # VALIDATE
                        querystring = urllib.unquote_plus(re.split("[?,/,#,&]+q=",msg.request.path)[1].split('&')[0])
                        
                        lastrowid = c.lastrowid
                        
                        row = (True,lastrowid)
                        c.execute("UPDATE ui_webrequest set issearch = ? where id = ?;",row)
                        
                        row = (lastrowid,querystring)
                        c.execute("INSERT INTO ui_websearch (webrequest_id,query) values (?,?);",row)
                        conn.commit()
                        print "Inserted search #{0}: {1}.".format(lastrowid,querystring)
                        
                # do the same thing for bing, other places where kids could search for bad stuff
                        
                    
            conn.close()
			
    	#elif (msg.code < 300):
    		# not a jpeg, not text/html, not a redirect
    		#print "[{0}]-> [{1}] {2}://{3}{4}".format(msg.code,msg.headers["Content-Type"],msg.request.scheme,msg.request.host,msg.request.path)

config = proxy.ProxyConfig(cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
)
server = proxy.ProxyServer(config, 8080)
m = SbxMaster(server)
m.run()

