from modulector.exceptions.exceptions import SourceNotPresentException
from modulector.models import MirnaSource
from modulector.processors import mirdb_processor, i2d_processor
from modulector.services import data_loading_service

processors = {
    "mirdb": mirdb_processor,
    "I2D": i2d_processor
}


def execute(source_id: int):
    data_loading_service.load_data()
    mirna_source = MirnaSource.objects.get(id=source_id)
    if mirna_source:
        processor = processors.get(mirna_source.name)
        processor.process(mirna_source=mirna_source)
    else:
        raise SourceNotPresentException(source_id=source_id)
