from abc import ABC, abstractmethod


class BaseReportGenerator(ABC):
    @abstractmethod
    def get_information():
        pass
    
    @abstractmethod
    def parse_information():
        pass
    
    @abstractmethod
    def generate_report_summary():
        pass
    
    @abstractmethod
    def convert_summary_to_audio():
        pass
    
    @abstractmethod
    def generate_report():
        pass