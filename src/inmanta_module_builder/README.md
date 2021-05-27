# Inmanta module builder

This package contains a few python classes that represents components of an inmanta module:
 - `Entity`: Represents an `entity` definition.
 - `Implem`: Represents an `implem` statement.
 - `Implementation`: Represents an `implementation` definition.
 - `EntityRelation`: Represents an relation between two entities.
 - `Index`: Represents an `index` statement.
 - `Attribute`: Represents an entity attribute.
 - `Module`: Represents the module itself.
 - `Plugin`: Represents a plugin.

All those classes can be instantiated and passed to an `InmantaModuleBuilder` instance to generate a module.  The module generation will build all required model files, the plugin file, and a simple test.

**Tips**  The path attribute that most of the previously mentioned classes take in their constructor can be used to specify where in the module the element should be located.  The path is a list of string.  
If an entity has as path: `["test", "a", "b"]` and as name: `C`, the entity will will be placed in the module `test` in the file `model/a/b/_init.cf` (starting from the root of the module).  To import it, you will then use the following statement: `import test::a::b`, and to use it: `test::a::b::C(...)`.

## Example

```python
from inmanta_module_builder.inmanta.attribute import Attribute, InmantaPrimitiveList
from inmanta_module_builder.inmanta.entity import Entity
from inmanta_module_builder.inmanta.entity_relation import EntityRelation
from inmanta_module_builder.inmanta.implement import Implement
from inmanta_module_builder.inmanta.implementation import Implementation
from inmanta_module_builder.inmanta.index import Index
from inmanta_module_builder.inmanta.module import Module
from inmanta_module_builder.inmanta_module_builder import InmantaModuleBuilder


module = Module(name="test")
module_builder = InmantaModuleBuilder(
    module, Path("/home/guillaume/Documents/terraform-dev/libs/")
)

entity = Entity(
    "Test",
    path=[module.name],
    attributes=[
        Attribute(
            name="test",
            inmanta_type=InmantaPrimitiveList("string"),
            default="[]",
            description="This is a test attribute",
        )
    ],
    description="This is a test entity",
)

implementation = Implementation(
    name="test",
    path=[module.name],
    entity=entity,
    content="",
    description="This is a test implementation",
)

implement = Implement(
    path=[module.name],
    implementation=implementation,
    entity=entity,
)

index = Index(
    path=[module.name],
    entity=entity,
    attributes=entity.attributes,
    description="This is a test index",
)

relation = EntityRelation(
    name="tests",
    path=[module.name],
    entity=entity,
    arity=(0, None),
    peer=EntityRelation(
        name="",
        path=[module.name],
        entity=entity,
        arity=(0, 0),
    ),
)

module_builder.add_module_element(entity)
module_builder.add_module_element(implementation)
module_builder.add_module_element(implement)
module_builder.add_module_element(index)
module_builder.add_module_element(relation)

module_builder.generate_module(True)
```


## Recommended usage
Even though this package can be used standalone to generate module, it is very verbose and it probably takes more time to generate a module manually with it than directly writing it in Inmanta language.  This module is meant to be used with any other tool to generate module automatically (from some schema input, that logic has to be handled by the parser using this package).

An example of such usage is the terraform module generator, which parse the schema of a terraform provider and convert it to the previously presented objects.  The module builder can then be used to generate the inmanta module.
