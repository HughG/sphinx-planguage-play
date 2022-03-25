from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
# from sphinx.domains.python import _pseudo_parse_arglist
from sphinx.locale import _
from sphinx.roles import XRefRole
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.docfields import DocFieldTransformer
from sphinx.util.nodes import make_refnode


from sphinx.util import logging # Load on top of python's logging module
logger = logging.getLogger(__name__)
logger.info('Hello, this is an extension!')

# MOD_SEP = '::'

def setup(app):
    # app.add_config_value('coffee_src_dir', None, 'env')
    # app.add_config_value('coffee_src_parser', None, 'env')
    # # # from .domain import PlanguageDomain
    app.add_domain(PlanguageDomain)

    directives.register_directive('_PLO', PlanguageObject)

# Copied from sphinx/util/docfields.py
def _is_single_paragraph(node):
    # type: (nodes.Node) -> bool
    """True if the node only contains one paragraph (and system messages)."""
    if len(node) == 0:
        return False
    elif len(node) > 1:
        for subnode in node[1:]:
            if not isinstance(subnode, nodes.system_message):
                return False
    if isinstance(node[0], nodes.paragraph):
        return True
    return False

# Copied from sphinx/util/docfields.py
class PlanguageDocFieldTransformer(DocFieldTransformer):

    def transform(self, node):
        # type: (nodes.Node) -> None
        """Transform a single field list *node*."""
        typemap = self.typemap

        ####raise Exception('Here!')

        entries = []
        groupindices = {}  # type: Dict[unicode, int]
        types = {}  # type: Dict[unicode, Dict]

        # step 1: traverse all fields and collect field types and content
        for field in node:
            fieldname, fieldbody = field
            try:
                # split into field type and argument
                fieldtype, fieldarg = fieldname.astext().split(None, 1)
            except ValueError:
                # maybe an argument-less field type?
                fieldtype, fieldarg = fieldname.astext(), ''
            typedesc, is_typefield = typemap.get(fieldtype, (None, None))

            # collect the content, trying not to keep unnecessary paragraphs
            if _is_single_paragraph(fieldbody):
                content = fieldbody.children[0].children
            else:
                content = fieldbody.children

            ###HACK
            print('Field %s content is (%s) >%s<' % (fieldname, len(content), content))
            if not content:
                continue

            # sort out unknown fields
            if typedesc is None or typedesc.has_arg != bool(fieldarg):
                # either the field name is unknown, or the argument doesn't
                # match the spec; capitalize field name and be done with it

                print('Unknown field >%s<' % (field))


                new_fieldname = fieldtype[0:1].upper() + fieldtype[1:]
                if fieldarg:
                    new_fieldname += ' ' + fieldarg
                fieldname[0] = nodes.Text(new_fieldname)
                entries.append(field)
                continue

            typename = typedesc.name

            # # collect the content, trying not to keep unnecessary paragraphs
            # if _is_single_paragraph(fieldbody):
                # content = fieldbody.children[0].children
            # else:
                # content = fieldbody.children

            # ###HACK
            # print('Field %s content is >%s<' % (fieldname, content))

            # if the field specifies a type, put it in the types collection
            if is_typefield:
                # filter out only inline nodes; others will result in invalid
                # markup being written out
                content = [n for n in content if isinstance(n, nodes.Inline) or
                           isinstance(n, nodes.Text)]
                if content:
                    types.setdefault(typename, {})[fieldarg] = content
                continue

            # also support syntax like ``:param type name:``
            if typedesc.is_typed:
                try:
                    argtype, argname = fieldarg.split(None, 1)
                except ValueError:
                    pass
                else:
                    types.setdefault(typename, {})[argname] = \
                        [nodes.Text(argtype)]
                    fieldarg = argname

            translatable_content = nodes.inline(fieldbody.rawsource,
                                                translatable=True)
            translatable_content.document = fieldbody.parent.document
            translatable_content.source = fieldbody.parent.source
            translatable_content.line = fieldbody.parent.line
            translatable_content += content

            # grouped entries need to be collected in one entry, while others
            # get one entry per field
            if typedesc.is_grouped:
                if typename in groupindices:
                    group = entries[groupindices[typename]]
                else:
                    groupindices[typename] = len(entries)
                    group = [typedesc, []]
                    entries.append(group)
                entry = typedesc.make_entry(fieldarg, [translatable_content])
                group[1].append(entry)
            else:
                entry = typedesc.make_entry(fieldarg, [translatable_content])
                entries.append([typedesc, entry])

        # step 2: all entries are collected, construct the new field list
        new_list = nodes.field_list()
        for entry in entries:
            if isinstance(entry, nodes.field):
                # pass-through old field
                new_list += entry
            else:
                fieldtype, content = entry
                fieldtypes = types.get(fieldtype.name, {})
                env = self.directive.state.document.settings.env
                new_list += fieldtype.make_field(fieldtypes, self.directive.domain,
                                                 content, env=env)

        node.replace_self(new_list)


class PlanguageObject(ObjectDescription):
    #: What is displayed right before the documentation entry.
    display_prefix = None # type: unicode

    doc_field_types = [
        Field('gist', label='Gist', names=('gist')),
        Field('description', label='Description', names=('desc', 'description')),
        Field('owner', label='Owner', names=('owner')),
        Field('source', label='Source', names=('source')),
        Field('author', label='Author', names=('author')),
    ]

    def handle_signature(self, sig, signode):
        # type: (unicode, addnodes.desc_signature) -> Tuple[unicode, unicode]
        """Breaks down construct signatures

        Parses out prefix and argument list from construct definition. The
        namespace and class will be determined by the nesting of domain
        directives.
        """
        if self.display_prefix:
            signode += addnodes.desc_annotation(self.display_prefix, self.display_prefix)
        
        signode += addnodes.desc_name(sig, sig)

        logger.critical('handle_signature')

        return sig

    def add_target_and_index(self, fqn, sig, signode):
        #doc = self.state.document
        if fqn not in self.state.document.ids:
            signode['names'].append(fqn)
            signode['ids'].append(fqn)
            self.state.document.note_explicit_target(signode)
        objects = self.env.domaindata['planguage']['objects']
        objects[fqn] = (self.env.docname, self.objtype)

        indextext = "%s (%s)" % (fqn, self.display_prefix.strip())
        self.indexnode['entries'].append(('single', _(indextext), fqn, '', None))

    def transform_content(self, contentnode: addnodes.desc_content) -> None:
        """
        Called after creating the content through nested parsing,
        but before the ``object-description-transform`` event is emitted,
        and before the info-fields are transformed.
        Can be used to manipulate the content.
        """
        PlanguageDocFieldTransformer(self).transform_all(contentnode)


class PlanguageFunctionRequirement(PlanguageObject):
    display_prefix = 'Function Requirement '

    doc_field_types = [
        Field('test', label='Test', names=('test')),
    ]


class PlanguagePerformanceRequirement(PlanguageObject):
    display_prefix = 'Performance Requirement '

    doc_field_types = [
        Field('scale', label='Scale', names=('scale')),
        GroupedField('level', label='Levels', names=('level', 'levels')),
        Field('meter', label='Meter', names=('meter')),
    ]


class PlanguageQualifier(PlanguageObject):
    display_prefix = 'Qualifier '


class PlanguageDesignIdea(PlanguageObject):
    display_prefix = 'Design Idea '

    doc_field_types = [
        GroupedField('impacts', label='Impacts', names=('impact', 'impacts')),
        GroupedField('impact_est', label='Impact Estimation', names=('ie', 'impact_est', 'impactest')),
    ]



# # PlanguageModule inherits from Directive to allow it to output titles etc.
# class PlanguageModule(Directive):
    # domain = 'planguage'
    # required_arguments = 1
    # has_content = True

    # def run(self):
        # env = self.state.document.settings.env
        # modname = self.arguments[0].strip()
        # noindex = 'noindex' in self.options
        # env.temp_data['planguage:module'] = modname
        # if noindex:
            # return []
        # env.domaindata['planguage']['modules'][modname] = \
            # (env.docname, self.options.get('synopsis', ''),
             # self.options.get('platform', ''), 'deprecated' in self.options)
        # # make a duplicate entry in 'objects' to facilitate searching for
        # # the module in PlanguageDomain.find_obj()
        # env.domaindata['planguage']['objects'][modname] = (env.docname, 'module')
        # targetnode = nodes.target('', '', ids=['module-' + modname],
                                  # ismod=True)
        # self.state.document.note_explicit_target(targetnode)
        # indextext = _('%s (module)') % modname[:-2]
        # inode = addnodes.index(entries=[('single', indextext,
                                         # 'module-' + modname, '')])
        # return [targetnode, inode]


# class PlanguageClass(PlanguageObj):
    # option_spec = {
        # 'module': directives.unchanged,
        # 'export_name': directives.unchanged,
        # 'parent': directives.unchanged,
    # }

    # display_prefix = 'class '

    # def handle_signature(self, sig, signode):
        # fullname = super(PlanguageClass, self).handle_signature(sig, signode)

        # parent = self.options.get('parent')
        # if parent:
            # signode += addnodes.desc_annotation('extends', ' extends ')
            # modname, classname = parent.split(MOD_SEP)
            # pnode = addnodes.pending_xref(classname,
                                          # refdomain='planguage',
                                          # reftype='class',
                                          # reftarget=parent,
                                          # )
            # pnode += nodes.literal(classname,
                                   # classname,
                                   # classes=['xref',
                                            # 'planguage',
                                            # 'planguage-class'])
            # signode += pnode

        # return fullname

class PlanguageXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        """ Called after PlanguageDomain.resolve_xref """
        # if not has_explicit_title:
            # title = title.split(MOD_SEP).pop()
        return title, target


class PlanguageDomain(Domain):

    label = 'Planguage'
    name = 'planguage'
    object_types = {
        'freq': ObjType(_('freq'), 'freq'),
        'preq': ObjType(_('preq'), 'preq'),
        'qual': ObjType(_('qual'), 'qual'),
        'design': ObjType(_('design'), 'design'),
    }

    directives = {
        'freq': PlanguageFunctionRequirement,
        'preq': PlanguagePerformanceRequirement,
        'qual': PlanguageQualifier,
        'design': PlanguageDesignIdea,
    }

    roles = {
        'fr': PlanguageXRefRole(),
        'pr': PlanguageXRefRole(),
        'q': PlanguageXRefRole(),
        'di': PlanguageXRefRole(),
    }

    data_version = 1
    initial_data = {"modules": {}, "objects": {}}

    def get_objects(self):
        logger.critical('get_objects')

        for fqn, (docname, objtype) in list(self.data['objects'].items()):
            yield (fqn, fqn, objtype, docname, fqn, 1)

    def resolve_xref(self, env, fromdocname, builder, type, target, node, contnode):
        if target[0] == '~':
            target = target[1:]
        doc, _ = self.data['objects'].get(target, (None, None))
        if doc:
            return make_refnode(builder, fromdocname, doc, target, contnode,
                                target)
