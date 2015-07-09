#/usr/bin/python
import re
import textwrap
import os

print "[LOG] Copying necessary source files..."
os.system("cp -rf sfc/openstack_dashboard/project/* /usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/")
os.system("cp -rf sfc/openstack_dashboard/api/sfc.py /usr/share/openstack-dashboard/openstack_dashboard/api/")

def apply_patch(path, line_pattern, pattern, replace_str, before=False):
   text = open( path ).read()
   match_found=False
   matches = re.finditer(line_pattern, text)
   m = None      # optional statement. just for clarification
   for m in matches:
      match_found=True
      pass       # just loop to the end
   
   if (match_found):
      m.start()  
      m.end()    
      exists = re.search(pattern, text)
      if not exists:
         if before:
            text1 = text[0:m.start()] + replace_str + text[(m.start()):]
         else:
            text1 = text[0:m.end()] + replace_str + text[(m.end()+0):]
         f = open(path, 'w+')
         f.write(text1)
         print "[PATCHED] Patched File '%s' with...'%s'" % (str(path), str(replace_str))
         f.close()
      else:
         print "[IGONORED] Patch Igonred for the file '%s': '%s' already there..." % (str(path), str(pattern))

print "[LOG] Patching Openstack Dashboard for SFC..."

####
path = '/usr/share/openstack-dashboard/openstack_dashboard/api/__init__.py'
line_pattern = r'from openstack_dashboard.api import \w+'
pattern = 'from openstack_dashboard.api import sfc'
replace_str = textwrap.dedent("""
                              from openstack_dashboard.api import sfc
                              """)
apply_patch(path, line_pattern, pattern, replace_str)

####
line_pattern = r'"\w+"\,'
pattern = '"sfc",'
replace_str = "\n    " + '"sfc",'
apply_patch(path, line_pattern, pattern, replace_str)

####
path = '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/dashboard.py'
replace_str = 'class NetworkServicePanels(horizon.PanelGroup):\n'
replace_str = replace_str + '    slug = "network-infra"\n'
replace_str = replace_str + '    name = _("Network Services")\n'
replace_str = replace_str + "    panels = ('networkfunctions',\n"
replace_str = replace_str + "              'categories',\n"
replace_str = replace_str + "              'configurations',\n"
replace_str = replace_str + "              'vendors',\n"
replace_str = replace_str + "              'appliances',\n"
replace_str = replace_str + "              'chains',\n"
replace_str = replace_str + "              'chainsets',\n"
replace_str = replace_str + "              'chainmaps',\n"
replace_str = replace_str + "              'nfdelta',\n"
replace_str = replace_str + "              'crd_topology')\n\n"
line_pattern = r'class Project\(horizon\.Dashboard\)'
pattern = 'class NetworkServicePanels'
apply_patch(path, line_pattern, pattern, replace_str, before=True)

####
replace_str = '\n        NetworkServicePanels,'
line_pattern = r'Panels,'
pattern = 'NetworkServicePanels,'
apply_patch(path, line_pattern, pattern, replace_str)
