from modulector.exceptions.exceptions import SourceNotPresentException
from modulector.models import MirnaSource
from modulector.processors import mirdip_processor
from modulector.services import data_loading_service

processors = {
    "mirdip": mirdip_processor
}


def execute(source_name: str):
    data_loading_service.load_data()
    mirna_source = MirnaSource.objects.get(name=source_name)
    if mirna_source:
        processor = processors.get(mirna_source.name)
        processor.process(mirna_source=mirna_source)
    else:
        raise SourceNotPresentException(source=source_name)
