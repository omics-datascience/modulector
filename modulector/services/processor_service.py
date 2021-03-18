from modulector.exceptions.exceptions import CommandNotPresentException
from modulector.mappers import mature_mirna_mapper, ref_seq_mapper, gene_mapper
from modulector.processors import mirdip_processor, drugs_processor, disease_processor, sequence_processor

commands_map = {
    "drugs": drugs_processor,
    "mature_mirna": mature_mirna_mapper,
    "diseases": disease_processor,
    "ref_seq": ref_seq_mapper,
    "gene": gene_mapper,
    "sequence": sequence_processor,
    "mirdip": mirdip_processor
}


def validate_processing_parameters(request):
    commands = request.query_params.get("commands").split(",")
    if commands:
        for command in commands:
            if command not in commands_map.keys():
                raise CommandNotPresentException(command=command, commands_list=list(commands_map))
    return commands


def execute(commands):
    if commands:
        for command in commands:
            commands_map.get(command).process()
    else:
        for command in commands_map.values():
            command.process()
