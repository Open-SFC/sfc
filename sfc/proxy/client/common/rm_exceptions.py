# Copyright 2013 Freescale Semiconductor, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
SFCProxy base exception handling.
"""

from oslo_i18n._i18n import _

class SFCProxyException(Exception):
    """Base SFC Proxy Exception
    """
    message = _("An unknown exception occurred.")

    def __init__(self, **kwargs):
        try:
            self._error_string = self.message % kwargs

        except Exception:
            self._error_string = self.message

    def __str__(self):
        return self._error_string
    
class SFCProxyClientException(SFCProxyException):

    def __init__(self, **kwargs):
        message = kwargs.get('message')
        self.status_code = kwargs.get('status_code', 0)
        if message:
            self.message = message
        super(SFCProxyClientException, self).__init__(**kwargs)
        
class Unauthorized(SFCProxyClientException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    message = _("Unauthorized: bad credentials.")
    
class ConnectionFailed(SFCProxyClientException):
    message = _("Connection to ucm wsgi failed: %(reason)s")

class Error(Exception):
    def __init__(self, message=None):
        super(Error, self).__init__(message)
        
class Invalid(Error):
    pass

class InvalidContentType(Invalid):
    message = _("Invalid content type %(content_type)s.")

class MalformedRequestBody(SFCProxyException):
    message = _("Malformed request body: %(reason)s")
    
class CommandError(Exception):
    pass
    
    
