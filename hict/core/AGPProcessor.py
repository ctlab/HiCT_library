from typing import Tuple, List, Dict, Optional
from hict.core.common import ContigDirection
from typing import NamedTuple, List


class AGPScaffoldRecord(NamedTuple):
    name: str
    start_ctg: str
    end_ctg: str
    

class AGPContigRecord(NamedTuple):
    name : str
    direction : ContigDirection
    length : int


class AGPparser(object):
    def __init__(
        self,
        filename: str,
    ) -> None:
        self.contig_records_list : List[AGPContigRecord] = list()
        self.scaffold_records_list : List[AGPScaffoldRecord] = list()
        self.parseAGP(filename)
            
    def parseAGPLine(self, line: str) -> Tuple[str, str, str, int]:
        toks : List[str] = line.split()
        if toks[4] == 'N':
            gap_len : str = toks[5]
            return ('N_spacer', gap_len, '', 0)
        elif toks[4] == 'W':
            seq_object_name : str = toks[0]
            component_name : str = toks[5]
            component_direction : str = toks[8]
            component_len : int = int(toks[7])
            return (seq_object_name, component_name, component_direction, component_len)
        else:
            raise Exception(f'unexpected symbol in agp component_type column: {toks[4]}')
    
    def parseAGP(self, filename):
        with open(filename, 'r') as agp_file:
            scaf_name : str
            cur_scaf_name : str
            start_ctg : str
            end_ctg : str
            ctg_name : str
            ctg_dir : str
            ctg_len : int
            for i, line in enumerate(agp_file):
                scaf_name, ctg_name, ctg_dir, ctg_len = self.parseAGPLine(line)
                if scaf_name == 'N_spacer':
                    continue
                if ctg_dir not in ("+", "-"):
                    raise Exception(f'unexpected symbol in agp direction column: {ctg_dir}')
                ctg_dir = ContigDirection(1) if ctg_dir == '+' else ContigDirection(0)
                self.contig_records_list.append(AGPContigRecord(ctg_name, ctg_dir, ctg_len))
                if i == 0:
                    cur_scaf_name = scaf_name
                    start_ctg = ctg_name
                    end_ctg = ctg_name
                else:
                    if scaf_name == cur_scaf_name:
                        end_ctg = ctg_name
                    else:
                        self.scaffold_records_list.append(AGPScaffoldRecord(cur_scaf_name, start_ctg, end_ctg))
                        cur_scaf_name = scaf_name
                        start_ctg = ctg_name
                        end_ctg = ctg_name
            self.scaffold_records_list.append(AGPScaffoldRecord(cur_scaf_name, start_ctg, end_ctg))
             
    def getAGPContigRecords(self) -> List[AGPContigRecord]:
        return self.contig_records_list
    
    def getAGPScaffoldRecords(self) -> List[AGPScaffoldRecord]:
        return self.scaffold_records_list