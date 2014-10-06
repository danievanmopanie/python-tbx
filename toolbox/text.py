#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2013 - Ronan Delacroix
Text Utils
:author: Ronan Delacroix
"""

import cgi
import json
import datetime

import os
import lxml.etree as etree
import re
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import Encoders


def xml_get_tag(xml, tag, parent_tag = None, multi = False):
    """
    Returns the tag data for the first instance of the named
    tag, or for all instances if multi is true. If a parent tag
    is specified, then that will be required before the tag.
    """
    expr_str = '[<:]'+tag+'.*?>(?P<matched_text>.+?)<'
    if parent_tag:
        expr_str = '[<:]'+parent_tag+'.*?>.*?' + expr_str
    expr = re.compile(expr_str, re.DOTALL | re.IGNORECASE)
    if multi:
        return expr.findall(xml)
    else:
        if expr.search(xml):
            return expr.search(xml).group('matched_text').strip()
        else:
            None


def convert_to_unicode(text_to_convert):
    if type(text_to_convert)==unicode:
        for encoding in ['latin_1', 'ascii', 'utf-8']:
            try:
                strtext = text_to_convert.encode(encoding)
            except:
                pass
            else:
                break
        text_to_convert = strtext
        
    unitext = text_to_convert
    for encoding in ['utf-8', 'ascii', 'latin_1']:
        try:
            unitext = text_to_convert.decode(encoding)
        except:
            pass
        else:
            break
    return unitext


def convert_foreign_chars(text):
    text = text.replace(u'á', 'a')
    text = text.replace(u'ä', 'a')
    text = text.replace(u'å', 'a')
    text = text.replace(u'ç', 'c')
    text = text.replace(u'è', 'e')
    text = text.replace(u'é', 'e')
    text = text.replace(u'ê', 'e')
    text = text.replace(u'í', 'i')
    text = text.replace(u'ô', 'o')
    text = text.replace(u'ö', 'o')
    text = text.replace(u'ø', 'o')
    text = text.replace(u'Ø', 'O')
    text = text.replace(u'ü', 'u')
    text = text.replace(u'Ü', 'U')
    
    text = text.replace(u'æ', 'ae')
    
    text = text.replace(u'¬', '-')
    text = text.replace(u'£', '-')

    text = text.replace(u' & ', '-')
    text = text.replace(u' &', '-')
    text = text.replace(u'& ', '-')
    text = text.replace(u'&', '-')
    text = text.replace(u'@', '-')
    text = text.replace(u'[', '-')
    text = text.replace(u']', '-')
    
    return text


def javascript_quote(s, quote_double_quotes=True):
    """
    Escape characters for javascript strings.
    """
    ustring_re = re.compile(u"([\u0080-\uffff])")

    def fix(match):
        return r"\u%04x" % ord(match.group(1))

    if type(s) == str:
        s = s.decode('utf-8')
    elif type(s) != unicode:
        raise TypeError(s)
    s = s.replace('\\', '\\\\')
    s = s.replace('\r', '\\r')
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    s = s.replace("'", "\\'")
    if quote_double_quotes:
        s = s.replace('"', '&quot;')
    return str(ustring_re.sub(fix, s))

def send_mail(send_from, send_to, subject, text, server, files=None):
    if files==None:
        files=[]

    assert type(send_to)==list
    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text, 'html') )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        fp = open(f,"rb")
        fcontent = fp.read()
        part.set_payload( fcontent )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
        
def format_money(money):
    split_float = str(money).split(".")
    money_out = ""
    if len(split_float)==1:
        money_out = split_float[0] + ".00"
    else:
        if len(split_float[1])>1:
            money_out = split_float[0] + "." + split_float[1][:2]
        else:
            money_out = split_float[0] + "." + split_float[1] + "0"
        if money_out<=0:
            money_out = 0.01
    return money_out;


def seconds_from_hms( timestring ): # hh:mm:ss.fraction
    a = timestring.split( ':' )
    hours = int(a[0])
    minutes = int(a[1])
    secs = float(a[2])
    return ( hours * 3600 + minutes * 60 + secs )

    
def hours_minutes_seconds_verbose( seconds ):
    t = seconds
    hrs = int( ( t / 3600 ) )
    mins = int( ( t / 60 ) % 60 )
    secs = t % 60
    return ' '.join([
        (hrs + ' hour'+ ('s' if hrs > 1 else '') ) if hrs > 0 else '',
        (mins + ' minute'+ ('s' if mins > 1 else '') ) if mins > 0 else '',
        (secs + ' second'+ ('s' if secs > 1 else '') ) if secs > 0 else ''
    ])


def hms_from_seconds( seconds ):
    hours = int( seconds / 3600.0 )
    minutes = int( ( seconds / 60.0 ) % 60.0 )
    secs = int(seconds % 60.0)
    return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, secs)

def str2bool(v):
    return str(v).lower() in ("yes", "on", "true", "y", "t", "1")


dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

render_xml = lambda _dict: dict_to_xml_string("xml", _dict)
render_json = lambda _dict: json.dumps(_dict, sort_keys=False, indent=4, default=dthandler)
render_html = lambda _dict: dict_to_html(_dict)
render_txt = lambda _dict: dict_to_plaintext(_dict)

mime_rendering_dict = {
    'text/html'        : render_html,
    'application/html' : render_html,
    'application/xml'  : render_xml,
    'application/json' : render_json,
    'text/plain'       : render_txt
}



# DICT TO XML FUNCTION
def _dict_to_xml_recurse(parent, dictitem):
    if isinstance(dictitem, list):
        dictitem = {'item' : dictitem}
    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.iteritems():
            if unicode(tag) == '_text':
                parent.text = unicode(child)
            elif type(child) is type([]):
                # iterate through the array and convert
                for listchild in child:
                    elem = etree.Element(tag)
                    parent.append(elem)
                    _dict_to_xml_recurse(elem, listchild)
            elif len(tag)==36 and tag[8]=='-' and tag[13]=='-': #if uuid is name of the element we try to cook up something nice to display in xml
                uuid = tag
                tag = parent.tag.replace('_list', '').replace('_dict', '')
                elem = etree.Element(tag, uuid=uuid)
                parent.append(elem)
                _dict_to_xml_recurse(elem, child)
            else:
                try:
                    elem = etree.Element(tag)
                except ValueError:
                    elem = etree.Element("element", unrecognized=tag)
                parent.append(elem)
                _dict_to_xml_recurse(elem, child)
    else:
        parent.text = unicode(dictitem)


def dict_to_xml(xmldict):
    """
    Converts a dictionary to an XML ElementTree Element
    """
    roottag = xmldict.keys()[0]
    root = etree.Element(roottag)
    _dict_to_xml_recurse(root, xmldict[roottag])
    return root


def dict_to_xml_string(root_name, _dict):
    _dict = {root_name : _dict}
    xml_root = dict_to_xml(_dict)
    return etree.tostring(xml_root, pretty_print=True, encoding="UTF-8", xml_declaration=True)


# DICT TO TEXT FUNCTION
def dict_to_plaintext(_dict, indent=0, result=''):
    if isinstance(_dict, list):
        i=0
        if _dict==[]:
            result += '\t' * indent + "<empty>\n"
        for value in _dict:
            i+=1
            if isinstance(value, dict) :
                result += '\t' * indent + "["+unicode(i)+"]={DICT}\n" + dict_to_plaintext(value, indent+1)
            elif isinstance(value, list) :
                result += '\t' * indent + "["+unicode(i)+"]=<LIST>\n" + dict_to_plaintext(value, indent+1) + "\n"
            else:
                result += '\t' * indent + "["+unicode(i)+"]=\"" + unicode(value) + "\"\n"
        return result
    elif isinstance(_dict, dict):
        for key, value in _dict.iteritems():
            if isinstance(value, dict):
                result += '\t' * indent + "{" + unicode(key) + "}\n" + dict_to_plaintext(value, indent+1)
            elif isinstance(value, list):
                result += '\t' * indent + "<" + unicode(key) + '>\n' + dict_to_plaintext(value, indent+1)
            else:
                if "\n" in unicode(value):
                    value = ' '.join([line.strip() for line in unicode(value).replace("\"", "'").split("\n")])
                result += '\t' * indent + unicode(key) + '=' + "\"" + unicode(value) + "\"\n"
        return result
    else:
        return "\"" + unicode(_dict) + "\""



# DICT TO HTML FUNCTION

def _dict_to_html_recurse(_dict, indent=0, result=''):
    if isinstance(_dict, list):
        i=0
        result += '    ' * indent + "<ul>\n"
        for value in _dict:
            i+=1
            if isinstance(value, dict) :
                result += '    ' * (indent+1) + "<li class='row"+unicode(i%2)+"'>\n" + _dict_to_html_recurse(value, indent+2) + '    ' * (indent+1) + "</li>\n"
            elif isinstance(value, list) :
                result += '    ' * (indent+1) + "<li class='row"+unicode(i%2)+"'>\n" + _dict_to_html_recurse(value, indent+2) + '    ' * (indent+1) + "</li>\n"
            else:
                result += '    ' * (indent+1) + "<li class='row"+unicode(i%2)+"'><pre>" + cgi.escape(unicode(value)) + "</pre></li>\n"
        result += '    ' * indent + "</ul>\n"
        return result
    elif isinstance(_dict, dict):
        result += '    ' * indent + "<table>\n"
        i=0
        for key, value in _dict.iteritems():
            i+=1
            if isinstance(value, dict) or isinstance(value, list):
                result += '    ' * (indent+1) + "<tr class='row"+unicode(i%2)+"'>\n"
                result += '    ' * (indent+2) + "<td>" + unicode(key) + "</td>\n"
                result += '    ' * (indent+2) + "<td>\n" + _dict_to_html_recurse(value, indent+3)
                result += '    ' * (indent+2) + "</td>\n"
                result += '    ' * (indent+1) + "</tr>\n"
            else:
                value = cgi.escape(unicode(value))
                result += '    ' * (indent+1) + "<tr class='row"+unicode(i%2)+"'><td>" + unicode(key) + "</td><td>" + "<pre>" + unicode(value) + "</pre></td></tr>\n"
        result += '    ' * indent + "</table>\n"
        return result
    else:
        return "<pre>" + cgi.escape(unicode(_dict)) + "</pre>"


def dict_to_html(_dict, title="Result"):
    return """
<html>
    <head>
        <style>
            body { font-family: monospace; }
            table { display : inline-block; border-spacing: 0px; border-collapse: collapse; }
            td { border : 1px solid grey; padding:3px 10px; }
            li { border : 1px solid grey; padding:0px 10px 0px 10px; margin: 0px 0px 0px 5px; list-style-type : circle; }
            ul { display : inline-block; padding:0px 0px 0px 10px; margin:0px;}
            pre { margin:0 ; }
            .row0 { background-color:#EAEAFF; }
            .row1 { background-color:#FFFFFF; }
        </style>
        <title>"""+title+"""</title>
    </head>
    <body>
""" + _dict_to_html_recurse(_dict, 2) + "    </body>\n</html>"


def test_page(title="Result"):
    result = "<table>"
    docu = {}
    i=0
    for func_name, doc in docu.items():
        result += "<tr class='row" + unicode(i) + "'><td>" + doc['friendly_name'] + "</td>"
        if 'parameters' in doc:
            result += "<td><form action='" + func_name + "' method='"+doc['method_type']+"' enctype='multipart/form-data'>"
            result += "<table width='100%'>"
            if 'required' in doc['parameters']:
                result += "<tr><th colspan='2'>Required</th></tr>"
                for param in doc['parameters']['required']:
                    if param == 'asset_file':
                        result += "<tr><td>" + unicode(param) + "</td><td><input type='file' name='" + unicode(param) + "' value=''/></td><tr/>"
                    else:
                        result += "<tr><td>" + unicode(param) + "</td><td><input type='text' name='" + unicode(param) + "' value=''/></td><tr/>"

            if 'optionnal' in doc['parameters']:
                result += "<tr><th colspan='2'>Optionnal</th></tr>"
                for param, value in doc['parameters']['optionnal'].items():
                    if value==None:
                        value=''
                    result += "<tr><td>" + unicode(param) + "</td><td><input type='text' name='" + unicode(param) + "' value='" + unicode(value) + "'/></td><tr/>"
            result += "<tr><th colspan='2'><input type='submit'/></th></tr>"
            result += "</table>"
            result += "</form></td>"
        else:
            result += "<td><a href='" + func_name + "'>" + func_name + "</a></td>"
        result += "</tr>"
        i += 1
        i = i%2

    result += "</table>"
    return """
<html>
    <head>
        <style>
            body { font-family: monospace; }
            table { display : inline-block; border-spacing: 0px; border-collapse: collapse; }
            td { border : 1px solid grey; padding:3px 10px; }
            li { border : 1px solid grey; padding:0px 10px 0px 10px; margin: 0px 0px 0px 5px; list-style-type : circle; }
            ul { display : inline-block; padding:0px 0px 0px 10px; margin:0px;}
            pre { margin:0 ; }
            .row0 { background-color:#EAEAFF; }
            .row1 { background-color:#FFFFFF; }
        </style>
        <title>"""+title+"""</title>
    </head>
    <body>
""" + result + "    </body>\n</html>"
