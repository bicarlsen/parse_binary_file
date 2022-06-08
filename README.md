# Parse Binary File

> Install with `python -m pip install parse_binary_file`

Parse binary files by describing their structure.

## Description file
The `parse_binary_file` package is based on the idea that binary file formats
should be parsed from a description of their format.

If the description file is a list, `pbf` assumes that the elemnts are fields.
One can also pass a dictionary, though, to describe more details about the file
format.

There are three top-level items that can be specified:
+ **`info`:** Describes information about the file as a whole (e.g. endianess).
+ **`default_options`:** Describes defaults options for each field type.
+ **`fields`:** Fields of the file format.

### Info
Describes information about the file.

#### Properties
+ **`byte_order`:** Byte order of the file. 
    Valid values: ['little', 'big', 'native']
    `native` byte ordering uses the byte ordering of the current machine.
    [Default: 'native']

+ **`encoding`:** File encoding.
    Used to encode the description file's values to bytes when matching against
    the file being parsed.
    See Python's [standard encodings](https://docs.python.org/3/library/codecs.html#standard-encodings)
    for valid values.
    [Default: 'utf-8']

+ **`word_size`:** Bytes per word of the file. [Default: 4 bytes]
    [Inactive]

### Default Options
Describes parsing information for each type of field.
All types can specify default values for a particular field property (discussed below).
To specify a default field property first specify the type of the field, then the property.

e.g.
To specify strings are null terminated (`\x00`) by default 
```yaml
default_options:
    str:
        terminator: "\x00"
```

### Fields
Describes the fields of the file format.
Each field must one and only one termination condition.
Termination conditions are determined by the `size`, `value`, and `terminator` fields.
for some types these can be interpreted. For instance, an `int` is assumed to
have a size of 4, so a termination condition does not need to be explicitly stated.

All fields can have the properties:
+ **`type`:** Data type of the field.
    If a type is enclosed in brackets (`[]`) it marks the field as an array-like field.
    Array like fields are assumed to contain multiple instances of the specified
    type. For more information see the **Array Fields** section.
+ **`size`:** Sets the size of the field in bytes. This may be inferred
    depending on the field's `type`.
    A size of `-1` indicated the field extends until the end of the file.
    Only the final field may have a length of `-1`.
+ **`value`:** Sets the size of the fiel based on the expected value.
+ **`format`:** How to format the field. This is type dependent.
    For `str` fields, this represents the encoding of the string and defaults to
    the file's encoding provided in the `info` section.
    For other types this represents how Python's [struct.unpack](https://docs.python.org/3/library/struct.html#struct-format-strings) should
    interpret the field.
+ **`terminator`:** Termination string.
+ **`is_null`:** Used for `bytes` data type to indicate all bytes should be null.
    Should be used in conjunction with the `size` property to indicate the
    termination condition.
+ **`name`:** Name of the field. Used for accessing the data by name.
+ **`description`:** Description of the field.
+ **`fields`:** Describes the subfields of the field.
    If a field is made up of subfields, its type must be `bytes` or `[bytes]`.
+ **`exec`:** Execution hooks for logical processing. [Inactive]

#### Type
If a field is not provided a type it defaults to `bytes`.

Valid types are:
+ **`bytes`:** Interpret the field as raw bytes. [Default]
+ **`char`:** Single character. (1 byte)
+ **`str`:** String data.
+ **`bool`:** Boolean. (1 byte)
+ **`short`:** Short integer. (2 bytes)
+ **`u_short`:** Unsigned short integer. (2 bytes)
+ **`int`:** Integer.(4 bytes)
+ **`u_int`:** Unisigned integer. (4 bytes)
+ **`long`:** Long integer. (1 word)
+ **`u_long`:** Unsigned long integer. (1 word)
+ **`long_long`:** Double long integer. (2 words)
+ **`u_long_long`:** Unsigned double long integer. (2 words)
+ **`float`:** Floating point number. (4 bytes)
+ **`double`:** Double precision floating point number. (2 words)
+ Any type may be wrapped in brackets `[]` to indicate the field is an array
    of that value type. Details of the elements are set using the `elements` property.
 
For more information read about Python [`struct`'s formatting strings](https://docs.python.org/3/library/struct.html#struct-format-strings). 

#### Termination condition
The termination condition of a field tells the parser how far to read.
There are three explicit and one implit termination condition.

##### Explicit
+ **`size`:** Sets the size of the field in bytes.
       This may be inferred depending on the field's `type`.
+ **`terminator`:** Termination string as bytes.
+ **`value`:** Sets the size of the field based on the expected value.

##### Implicit
+ **`subfields`:** [Inactive] The parent field can be terminated when the last child field is terminated.

#### Subfields
Each field can be made up of subfields. Each subfield follows the same pattern
as top-level fields. This is a recursive concept, so fields can be nested as
deeply as needed.

Fields that are made up of subfields must have their type set to `bytes` or
`[bytes]`.
If the type is `[bytes]` it is assumed that the subfields repeat in a array-like
manner with all sufields being repeated an equal number of times.
i.e. If the data for the parent field ends before all subfields have been read
an exception is raised.

#### Array Fields
A field may consist of multiple elements. This is where array fields come into
play. For instance, imagine a field that consists of a list of floats. To
indicate a field is array-like, enclose its type in square brackets ('[]')
(e.g. `[bytes]`, `[float]`).

#### Execution Hooks
> :warning: These fields allow arbitrary Python code to be executed.

It may be necessary to add some basic logic to your description.
For instance, if a field named `data` may have a variable length offset buffer
specified by a field named `data_offset`.
The `exec` field allows you to specify code before (`pre`) or after (`post`)
data for the field has been loaded and has access to all previous fields.
Each of these fields should contain a lambda function with signature
`(data, fields)` where `data` is byte string of the current field and 
`fields` is a `parse_binary_file.Data` object representing the file with
all previous fields loaded.


## Components

### FieldDescription
Describes a field.

#### Properties
+ **type:** The type of the field being described.
    When loading data into the field it will be parsed based on the type.
    +    [Default: 'bytes']

+ **name:** Name of the field.
    This is used to label the field.

+ **value:** The expected value of the field.
    This can be usedto indicate a specific value is expected for the field.

+ **size:** Number of bytes in the field.
    The last field can have a size of -1 which indicates the field continues to
    the end of the file.

+ **terminator:** Sequence of values indicating the end of the field.

+ **is_null:** Indicates the field only contains null bytes.
    Settings to true is equivalent to setting `value` equal to all null bytes.
    Must set `size` if `True`.

+ **description:** Description of the field.

+ **fields:** Used to specifiy the structure of the elements of an array.

#### Methods
+ **FieldDescription(\*\*properties):** Initializes a new `FieldDescription` with
  the provided properties.


### FileFormat
Container for `FieldDescription`s to describe the structure of a file.

#### Properties
+ **fields:** List of `FieldDescription`s.

+ **info:** Dictionary of information on the file.

+ Fields can be accessed by name or index using brackets (`[]`)

#### Methods
+ **from_dicts(desc, info, defaults):** `@staticmethod` Converts a list of dictionaries into a `FileFormat`.

+ **keys():** Returns a list of the keys of named fields.

### Parser
Used for parsing files in a given format.

#### Properties
+ **format:** A `FileFormat` used to parse files.

#### Methods
+ **parse(stream):** Returns a `Data` object representing the data from `stream`.

### Field
Contains information about a field, including its description and loaded value.

#### Properties
+ **desc:** `FieldDescription` that was used to create the `Field`.

+ **value:** Parsed value.

+ **expected_value:** `self.desc.value`. Provided for convenience.

+ **fields:** Tuple of children `Field`s.

+ **size:** If the `Field`'s value is set, returns its size.
    If the `Field`'s value has not yet been set return the `Field`'s expected size if available.

+ **data:** Original data as bytes.

+ **value_is_valid:** Whether the parsed value matches the expected value. If a specific `value` was not specified by the `FieldDescription` this will always return `True`.

+ Values of the `Field`'s `FieldDescription` are accessible as properties, as well. 

#### Methods
+ **Field(desc: FieldDescription, fields: tuple[Field]):** Initializes a new `Field`.
    `desc` should describe the field, and `fields` are the children `Field`s.

+ **from_data(data: bytes, desc: FieldDescription):** Creates a new `Field` using `desc` as its description to parse `data`.

+ **parse_data(val: bytes, \*\*options):** Sets the value of the `Field` based on its description and the provided value.


### Data
Represents data from a file.

#### Properties
+ **fields:** `Field`s containing the parsed data.

+ **is_loaded:** If data has been loaded yet.

+ **value:** Values of the parsed data.
   
+ **named_field_values:** Returns a dictionary of name-value pairs for named `Field`s.
    If multiple fields have the same name a tuple is returned with the values in
    order.

+ `Field`s are accessible by name and index using brackets (`[]`). If multiple `Field`s have the same name, they are returned as a tuple in order.


## Use
This library is intended to be used by describing the struture of a binary file
format in a configuration file. That file is then loaded and used to create a
`Data` instance. The `Data` instance can then `load()` data from a file and
assort it into the correct fields.

## Example
We would like to describe a new binary file format of `.msg`.
| Offset | Size | Name     | Description                                          |
| ------ | ---- | -------- | ---------------------------------------------------- |
| 0x00   | 0x02 | head     | `0xff 0x00` Indicates the file is a `.msg` file.     |
| 0x02   | 0x04 | size     | Total size of the file.                              |
| 0x06   | 0x04 |  --      | Null bytes to separate header from body.             |
| 0x0a   |  --  | greeting | Message greeting, null terminated.                   |
|  --    |  --  | message  | Message content.                                     |


We can describe this structure in a YAML file.
`msg.yaml`
```yaml
info:
    byte_order: 'little'

fields:
    - name: 'head'
      value: "\xff\x00"

    - type: 'int'
      name: 'file_size'
      description: 'Size of file in bytes'

    - size: 4
      is_null: true

    - type: 'str'
      terminator: "\x00"
      name: 'greeting'

    - type: 'str'
      size: -1
      name: 'message'
```

To read a `.msg` file we can use the description of it.
```python
import os
import yaml  # use pyyaml to load `msg.yaml`
import parse_binary_file as pbf


# load description
with open('msg.yaml') as f:
    msg_desc = yaml.safe_load(f)
    
# create file format
msg_format = pbf.FieldFormat.from_dicts(msg_desc['fields'], info = msg_desc['info'])

# create parser
parser = pbf.Parser(msg_format)

# create data
with open('my_message.msg', 'rb') as f:
    data = parser.parse(f)

is_corrupt = (data['file_size'] != os.path.getsize('my_message.msg'))
greeting = data['greeting'].value
message = data[-1].value
```