# Copyright 2012 OpenStack LLC.
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

import argparse
import logging
import re

from cliff import lister
from cliff import show

from nscs.crd_consumer.client.common import command
from nscs.crd_consumer.client.common import rm_exceptions as exceptions
from nscs.crd_consumer.client.common import utils

HEX_ELEM = '[0-9A-Fa-f]'
UUID_PATTERN = '-'.join([HEX_ELEM + '{8}', HEX_ELEM + '{4}',
                         HEX_ELEM + '{4}', HEX_ELEM + '{4}',
                         HEX_ELEM + '{12}'])


def find_resourceid_by_name_or_id(client, resource, name_or_id):
    obj_lister = getattr(client, "list_%ss" % resource)
    # perform search by id only if we are passing a valid UUID
    match = re.match(UUID_PATTERN, name_or_id)
    collection = resource + "s"
    if match:
        data = obj_lister(id=name_or_id, fields='id')
        if data and data[collection]:
            return data[collection][0]['id']
    return _find_resourceid_by_name(client, resource, name_or_id)


def _find_resourceid_by_name(client, resource, name):
    obj_lister = getattr(client, "list_%ss" % resource)
    data = obj_lister(name=name, fields='id')
    collection = resource + "s"
    info = data[collection]
    if len(info) > 1:
        msg = (_("Multiple %(resource)s matches found for name '%(name)s',"
               " use an ID to be more specific.") %
               {'resource': resource, 'name': name})
        raise exceptions.CrdClientException(
            message=msg)
    elif len(info) == 0:
        not_found_message = (_("Unable to find %(resource)s with name "
                               "'%(name)s'") %
                             {'resource': resource, 'name': name})
        # 404 is used to simulate server side behavior
        raise exceptions.CrdClientException(
            message=not_found_message, status_code=404)
    else:
        return info[0]['id']


def add_show_list_common_argument(parser):
    parser.add_argument(
        '-D', '--show-details',
        help='show detailed info',
        action='store_true',
        default=False, )
    parser.add_argument(
        '--show_details',
        action='store_true',
        help=argparse.SUPPRESS)
    parser.add_argument(
        '--fields',
        help=argparse.SUPPRESS,
        action='append',
        default=[])
    parser.add_argument(
        '-F', '--field',
        dest='fields', metavar='FIELD',
        help='specify the field(s) to be returned by server,'
        ' can be repeated',
        action='append',
        default=[])


def add_pagination_argument(parser):
    parser.add_argument(
        '-P', '--page-size',
        dest='page_size', metavar='SIZE', type=int,
        help=("specify retrieve unit of each request, then split one request "
              "to several requests"),
        default=None)


def add_sorting_argument(parser):
    parser.add_argument(
        '--sort-key',
        dest='sort_key', metavar='FIELD',
        action='append',
        help=("sort list by specified fields (This option can be repeated), "
              "The number of sort_dir and sort_key should match each other, "
              "more sort_dir specified will be omitted, less will be filled "
              "with asc as default direction "),
        default=[])
    parser.add_argument(
        '--sort-dir',
        dest='sort_dir', metavar='{asc,desc}',
        help=("sort list in specified directions "
              "(This option can be repeated)"),
        action='append',
        default=[],
        choices=['asc', 'desc'])


def add_extra_argument(parser, name, _help):
    parser.add_argument(
        name,
        nargs=argparse.REMAINDER,
        help=_help + ': --key1 [type=int|bool|...] value '
                     '[--key2 [type=int|bool|...] value ...]')


def is_number(s):
    try:
        float(s)  # for int, long and float
    except ValueError:
        try:
            complex(s)  # for complex
        except ValueError:
            return False

    return True


def parse_args_to_dict(values_specs):
    '''It is used to analyze the extra command options to command.

    Besides known options and arguments, our commands also support user to
    put more options to the end of command line. For example,
    list_nets -- --tag x y --key1 value1, where '-- --tag x y --key1 value1'
    is extra options to our list_nets. This feature can support V2.0 API's
    fields selection and filters. For example, to list networks which has name
    'test4', we can have list_nets -- --name=test4.

    value spec is: --key type=int|bool|... value. Type is one of Python
    built-in types. By default, type is string. The key without value is
    a bool option. Key with two values will be a list option.

    '''
    # -- is a pseudo argument
    values_specs_copy = values_specs[:]
    if values_specs_copy and values_specs_copy[0] == '--':
        del values_specs_copy[0]
    _options = {}
    current_arg = None
    _values_specs = []
    _value_number = 0
    _list_flag = False
    current_item = None
    for _item in values_specs_copy:
        if _item.startswith('--'):
            if current_arg is not None:
                if _value_number > 1 or _list_flag:
                    current_arg.update({'nargs': '+'})
                elif _value_number == 0:
                    current_arg.update({'action': 'store_true'})
            _temp = _item
            if "=" in _item:
                _item = _item.split('=')[0]
            if _item in _options:
                raise exceptions.CommandError(
                    "duplicated options %s" % ' '.join(values_specs))
            else:
                _options.update({_item: {}})
            current_arg = _options[_item]
            _item = _temp
        elif _item.startswith('type='):
            if current_arg is None:
                raise exceptions.CommandError(
                    "invalid values_specs %s" % ' '.join(values_specs))
            if 'type' not in current_arg:
                _type_str = _item.split('=', 2)[1]
                current_arg.update({'type': eval(_type_str)})
                if _type_str == 'bool':
                    current_arg.update({'type': utils.str2bool})
                elif _type_str == 'dict':
                    current_arg.update({'type': utils.str2dict})
                continue
        elif _item == 'list=true':
            _list_flag = True
            continue
        if not _item.startswith('--'):
            if (not current_item or '=' in current_item or
                _item.startswith('-') and not is_number(_item)):
                raise exceptions.CommandError(
                    "Invalid values_specs %s" % ' '.join(values_specs))
            _value_number += 1
        elif _item.startswith('--'):
            current_item = _item
            if '=' in current_item:
                _value_number = 1
            else:
                _value_number = 0
            _list_flag = False
        _values_specs.append(_item)
    if current_arg is not None:
        if _value_number > 1 or _list_flag:
            current_arg.update({'nargs': '+'})
        elif _value_number == 0:
            current_arg.update({'action': 'store_true'})
    _args = None
    if _values_specs:
        _parser = argparse.ArgumentParser(add_help=False)
        for opt, optspec in _options.iteritems():
            _parser.add_argument(opt, **optspec)
        _args = _parser.parse_args(_values_specs)
    result_dict = {}
    if _args:
        for opt in _options.iterkeys():
            _opt = opt.split('--', 2)[1]
            _opt = _opt.replace('-', '_')
            _value = getattr(_args, _opt)
            if _value is not None:
                result_dict.update({_opt: _value})
    return result_dict


def _merge_args(qCmd, parsed_args, _extra_values, value_specs):
    """Merge arguments from _extra_values into parsed_args.

    If an argument value are provided in both and it is a list,
    the values in _extra_values will be merged into parsed_args.

    @param parsed_args: the parsed args from known options
    @param _extra_values: the other parsed arguments in unknown parts
    @param values_specs: the unparsed unknown parts
    """
    temp_values = _extra_values.copy()
    for key, value in temp_values.iteritems():
        if hasattr(parsed_args, key):
            arg_value = getattr(parsed_args, key)
            if arg_value is not None and value is not None:
                if isinstance(arg_value, list):
                    if value and isinstance(value, list):
                        if type(arg_value[0]) == type(value[0]):
                            arg_value.extend(value)
                            _extra_values.pop(key)


def update_dict(obj, dict, attributes):
    for attribute in attributes:
        if hasattr(obj, attribute) and getattr(obj, attribute):
            dict[attribute] = getattr(obj, attribute)


class CrmCommand(command.OpenStackCommand):
    api = 'sdnofcfg'
    log = logging.getLogger(__name__ + '.CrmCommand')
    values_specs = []
    json_indent = None

    def get_client(self):
        return self.app.client_manager.rm

    def get_parser(self, prog_name):
        parser = super(CrmCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--request-format',
            help=_('the xml or json request format'),
            default='json',
            choices=['json', 'xml', ], )
        parser.add_argument(
            '--request_format',
            choices=['json', 'xml', ],
            help=argparse.SUPPRESS)

        return parser

    def format_output_data(self, data):
        # Modify data to make it more readable
        if self.resource in data:
            for k, v in data[self.resource].iteritems():
                if isinstance(v, list):
                    value = '\n'.join(utils.dumps(
                        i, indent=self.json_indent) if isinstance(i, dict)
                        else str(i) for i in v)
                    data[self.resource][k] = value
                elif isinstance(v, dict):
                    value = utils.dumps(v, indent=self.json_indent)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        return {}


class CreateCommand(CrmCommand, show.ShowOne):
    """Create a resource for a given tenant

    """

    api = 'sdnofcfg'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(CreateCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='TENANT_ID',
            help=_('the owner tenant ID'), )
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        self.add_known_arguments(parser)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        rm_client = self.get_client()
        rm_client.format = parsed_args.request_format
        _extra_values = parse_args_to_dict(self.values_specs)
        _merge_args(self, parsed_args, _extra_values,
                    self.values_specs)
        body = self.args2body(parsed_args)
        body[self.resource].update(_extra_values)
        obj_creator = getattr(rm_client,
                              "create_%s" % self.resource)
        if self.resource == 'subnet':
            _id = parsed_args.network_id
            data = obj_creator(_id, body)
        elif self.resource in ['chain_service', 'chain_bypass_rule']:
            _chain_id = parsed_args.chain_id
            data = obj_creator(_chain_id, body)
        elif self.resource in ['chain_selection_rule']:
            _chain_set_id = parsed_args.chain_set_id
            data = obj_creator(_chain_set_id, body)
        else:
            data = obj_creator(body)
        
        self.format_output_data(data)
        # {u'network': {u'id': u'e9424a76-6db4-4c93-97b6-ec311cd51f19'}}
        info = self.resource in data and data[self.resource] or None
        if info:
            print >>self.app.stdout, _('Created a new %s:' % self.resource)
        else:
            info = {'': ''}
        return zip(*sorted(info.iteritems()))


class UpdateCommand(CrmCommand):
    """Update resource's information
    """

    api = 'sdnofcfg'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(UpdateCommand, self).get_parser(prog_name)
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help='ID or name of %s to update' % self.resource)
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        rm_client = self.get_client()
        rm_client.format = parsed_args.request_format
        _extra_values = parse_args_to_dict(self.values_specs)
        _merge_args(self, parsed_args, _extra_values,
                    self.values_specs)
        body = self.args2body(parsed_args)
        if self.resource in body:
            body[self.resource].update(_extra_values)
        else:
            body[self.resource] = _extra_values
        if not body[self.resource]:
            raise exceptions.CommandError(
                "Must specify new values to update %s" % self.resource)
        #_id = find_resourceid_by_name_or_id(rm_client,
        #                                    self.resource,
        #                                    parsed_args.id)
        _id = parsed_args.id
        obj_updator = getattr(rm_client,
                              "update_%s" % self.resource)
        
        if self.resource == 'subnet':
            _network_id = parsed_args.network_id
            obj_updator(_network_id, _id, body)
        elif self.resource in ['chain_service', 'chain_bypass_rule']:
            _chain_id = parsed_args.chain_id
            obj_updator(_chain_id, _id, body)
        elif self.resource in ['chain_selection_rule']:
            _chain_set_id = parsed_args.chain_set_id
            obj_updator(_chain_set_id, _id, body)
        else:
            obj_updator(_id, body)
        
        print >>self.app.stdout, (
            _('Updated %(resource)s: %(id)s') %
            {'id': parsed_args.id, 'resource': self.resource})
        return


class DeleteCommand(CrmCommand):
    """Delete a given resource

    """

    api = 'sdnofcfg'
    resource = None
    log = None
    allow_names = False

    def get_parser(self, prog_name):
        parser = super(DeleteCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to delete'
        else:
            help_str = 'ID of %s to delete'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource)
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        print 'run(%s)' % parsed_args
        params = vars(parsed_args)
        rm_client = self.get_client()
        rm_client.format = parsed_args.request_format
        obj_deleter = getattr(rm_client,
                              "delete_%s" % self.resource)
        if self.allow_names:
            _id = find_resourceid_by_name_or_id(rm_client, self.resource,
                                                parsed_args.id)
        else:
            _id = parsed_args.id
        params = {'body':params}
        if self.resource == 'subnet':
            _network_id = parsed_args.network_id
            obj_deleter(_network_id, _id)
        elif self.resource in ['chain_service', 'chain_bypass_rule']:
            _chain_id = parsed_args.chain_id
            obj_deleter(_chain_id, _id)
        elif self.resource in ['chain_selection_rule']:
            _chain_set_id = parsed_args.chain_set_id
            obj_deleter(_chain_set_id, _id)
        else:
            obj_deleter(_id)
        
        print >>self.app.stdout, (_('Deleted %(resource)s: %(id)s')
                                  % {'id': parsed_args.id,
                                     'resource': self.resource})
        return


class ListCommand(CrmCommand, lister.Lister):
    """List resources that belong to a given tenant

    """
    api = 'sdnofcfg'
    resource = None
    log = None
    _formatters = {}
    list_columns = []
    unknown_parts_flag = True
    pagination_support = False
    sorting_support = False

    def get_parser(self, prog_name):
        parser = super(ListCommand, self).get_parser(prog_name)
        self.add_known_arguments(parser)
        add_show_list_common_argument(parser)
        if self.unknown_parts_flag:
            add_extra_argument(parser, 'filter_specs', 'filters options')
        if self.pagination_support:
            add_pagination_argument(parser)
        if self.sorting_support:
            add_sorting_argument(parser)
        return parser

    def args2search_opts(self, parsed_args):
        search_opts = {}
        if self.unknown_parts_flag:
            search_opts = parse_args_to_dict(parsed_args.filter_specs)
        fields = parsed_args.fields
        if parsed_args.fields:
            search_opts.update({'fields': fields})
        if parsed_args.show_details:
            search_opts.update({'verbose': 'True'})
        return search_opts

    def call_server(self, rm_client, search_opts, parsed_args):
        obj_lister = getattr(rm_client,
                             "list_%ss" % self.resource)
        if self.resource == 'subnet':
            _id = parsed_args.network_id
            data = obj_lister(_id, **search_opts)
        elif self.resource in ['chain_service', 'chain_bypass_rule']:
            _chain_id = parsed_args.chain_id
            data = obj_lister(_chain_id, **search_opts)
        elif self.resource in ['chain_selection_rule']:
            _chain_set_id = parsed_args.chain_set_id
            data = obj_lister(_chain_set_id, **search_opts)
        else:
            data = obj_lister(**search_opts)
        return data

    def retrieve_list(self, parsed_args):
        """Retrieve a list of resources from Crd server"""
        rm_client = self.get_client()
        rm_client.format = parsed_args.request_format
        _extra_values = parse_args_to_dict(self.values_specs)
        _merge_args(self, parsed_args, _extra_values,
                    self.values_specs)
        search_opts = self.args2search_opts(parsed_args)
        search_opts.update(_extra_values)
        if self.pagination_support:
            page_size = parsed_args.page_size
            if page_size:
                search_opts.update({'limit': page_size})
        if self.sorting_support:
            keys = parsed_args.sort_key
            if keys:
                search_opts.update({'sort_key': keys})
            dirs = parsed_args.sort_dir
            len_diff = len(keys) - len(dirs)
            if len_diff > 0:
                dirs += ['asc'] * len_diff
            elif len_diff < 0:
                dirs = dirs[:len(keys)]
            if dirs:
                search_opts.update({'sort_dir': dirs})
        data = self.call_server(rm_client, search_opts, parsed_args)
        collection = self.resource + "s"
        return data.get(collection, [])

    def extend_list(self, data, parsed_args):
        """Update a retrieved list.

        This method provides a way to modify a original list returned from
        the rm server. For example, you can add subnet cidr information
        to a list network.
        """
        pass

    def setup_columns(self, info, parsed_args):
        _columns = len(info) > 0 and sorted(info[0].keys()) or []
        if not _columns:
            # clean the parsed_args.columns so that cliff will not break
            parsed_args.columns = []
        elif parsed_args.columns:
            _columns = [x for x in parsed_args.columns if x in _columns]
        elif self.list_columns:
            # if no -c(s) by user and list_columns, we use columns in
            # both list_columns and returned resource.
            # Also Keep their order the same as in list_columns
            _columns = [x for x in self.list_columns if x in _columns]
        return (_columns, (utils.get_item_properties(
            s, _columns, formatters=self._formatters, )
            for s in info), )

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        data = self.retrieve_list(parsed_args)
        self.extend_list(data, parsed_args)
        return self.setup_columns(data, parsed_args)


class ShowCommand(CrmCommand, show.ShowOne):
    """Show information of a given resource

    """

    api = 'sdnofcfg'
    resource = None
    log = None
    allow_names = False

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        self.add_known_arguments(parser)
        add_show_list_common_argument(parser)
        if self.allow_names:
            help_str = 'ID or name of %s to look up'
        else:
            help_str = 'ID of %s to look up'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        rm_client = self.get_client()
        rm_client.format = parsed_args.request_format

        params = {}
        if parsed_args.show_details:
            params = {'verbose': 'True'}
        if parsed_args.fields:
            params = {'fields': parsed_args.fields}
        # (trinaths) adding Cluster and controller ID handling support - Start
        arg_dict = vars(parsed_args)
        if 'cluster_id' in arg_dict:
            params['cluster_id'] = parsed_args.cluster_id
        if 'controller_id' in arg_dict:
            params['controller_id'] = parsed_args.controller_id
        # (trinaths) adding Cluster and controller ID handling support - end    
        if self.allow_names:
            _id = find_resourceid_by_name_or_id(rm_client, self.resource,
                                                parsed_args.id)
        else:
            _id = parsed_args.id
        params = {'body':params}
        obj_shower = getattr(rm_client, "show_%s" % self.resource)
        if self.resource == 'subnet':
            _network_id = parsed_args.network_id
            data = obj_shower(_network_id, _id, **params)
        elif self.resource in ['chain_service', 'chain_bypass_rule']:
            _chain_id = parsed_args.chain_id
            data = obj_shower(_chain_id, _id, **params)
        elif self.resource in ['chain_selection_rule']:
            _chain_set_id = parsed_args.chain_set_id
            data = obj_shower(_chain_set_id, _id, **params)
        else:
            data = obj_shower(_id, **params)
        
        
        self.format_output_data(data)
        resource = data[self.resource]
        if self.resource in data:
            return zip(*sorted(resource.iteritems()))
        else:
            return None
