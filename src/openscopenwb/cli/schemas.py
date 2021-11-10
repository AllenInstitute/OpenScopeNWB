import argschema


class ArgExampleInputSchema(argschema.ArgSchema):
    log_level = argschema.fields.LogLevel(
        default="INFO",
        description="override  default value of 'ERROR'")
    my_file = argschema.fields.InputFile(
        required=True,
        description="an input file for this example module")
    my_float = argschema.fields.Float(
        required=False,
        default=3.1415,
        description="a float input with a defaul value")


class ArgExampleOutputSchema(argschema.schemas.DefaultSchema):
    my_file_hash = argschema.fields.Str(
        required=True,
        description="sha256 hash of input file")
    my_float_diff_from_pi = argschema.fields.Float(
        required=True,
        description="difference of input float from pi")
