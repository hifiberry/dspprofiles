#!/usr/bin/env python3
"""
DSP Params File Parser

This script reads a .params file and extracts cell names, parameter names, 
and parameter addresses from DSP configuration files.
"""

import re
import argparse
import csv
from typing import List, Dict, Tuple


class DSPParamsParser:
    """Parser for DSP .params files"""
    
    def __init__(self):
        self.parameters = []
    
    def parse_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Parse a .params file and extract parameter information
        
        Args:
            file_path: Path to the .params file
            
        Returns:
            List of dictionaries containing cell_name, parameter_name, and parameter_address
        """
        self.parameters = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Split content into parameter blocks
            blocks = self._split_into_blocks(content)
            
            for block in blocks:
                param_info = self._parse_block(block)
                if param_info:
                    self.parameters.append(param_info)
                    
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except Exception as e:
            print(f"Error reading file: {e}")
            
        return self.parameters
    
    def _split_into_blocks(self, content: str) -> List[str]:
        """Split the content into individual parameter blocks"""
        # Split by double newlines to separate parameter blocks
        blocks = re.split(r'\n\s*\n\s*\n', content)
        return [block.strip() for block in blocks if block.strip()]
    
    def _parse_block(self, block: str) -> Dict[str, str]:
        """
        Parse a single parameter block to extract information
        
        Args:
            block: Text block containing parameter information
            
        Returns:
            Dictionary with cell_name, parameter_name, parameter_address
        """
        lines = block.split('\n')
        param_info = {}
        
        for line in lines:
            line = line.strip()
            
            # Extract Cell Name
            if line.startswith('Cell Name'):
                match = re.search(r'Cell Name\s*=\s*(.+)', line)
                if match:
                    param_info['cell_name'] = match.group(1).strip()
            
            # Extract Parameter Name
            elif line.startswith('Parameter Name'):
                match = re.search(r'Parameter Name\s*=\s*(.+)', line)
                if match:
                    param_info['parameter_name'] = match.group(1).strip()
            
            # Extract Parameter Address
            elif line.startswith('Parameter Address'):
                match = re.search(r'Parameter Address\s*=\s*(\d+)', line)
                if match:
                    param_info['parameter_address'] = match.group(1).strip()
        
        # Only return if we have all required fields
        if all(key in param_info for key in ['cell_name', 'parameter_name', 'parameter_address']):
            return param_info
        
        return None
    
    def print_parameters(self):
        """Print all parsed parameters in a formatted table"""
        if not self.parameters:
            print("No parameters found.")
            return
        
        print(f"{'Cell Name':<40} {'Parameter Name':<50} {'Address':<10}")
        print("-" * 100)
        
        for param in self.parameters:
            print(f"{param['cell_name']:<40} {param['parameter_name']:<50} {param['parameter_address']:<10}")
    
    def print_address_lists(self):
        """Print cells with their combined address lists"""
        if not self.parameters:
            print("No parameters found.")
            return
        
        cell_addresses = self.get_cells_with_address_lists()
        
        print(f"{'Cell Name':<40} {'Address Count':<15} {'Addresses'}")
        print("-" * 100)
        
        for cell_name in sorted(cell_addresses.keys()):
            addresses = cell_addresses[cell_name]
            address_count = len(addresses)
            
            # Format addresses - show first few, then indicate if there are more
            if len(addresses) <= 10:
                address_str = ', '.join(addresses)
            else:
                address_str = ', '.join(addresses[:10]) + f", ... (+{len(addresses)-10} more)"
            
            print(f"{cell_name:<40} {address_count:<15} {address_str}")
    
    def print_address_ranges(self):
        """Print cells with their address ranges"""
        if not self.parameters:
            print("No parameters found.")
            return
        
        cell_ranges = self.get_cells_with_address_ranges()
        
        print(f"{'Cell Name':<40} {'Address Count':<15} {'Address Range'}")
        print("-" * 100)
        
        for cell_name in sorted(cell_ranges.keys()):
            range_info = cell_ranges[cell_name]
            address_count = range_info['count']
            min_addr = range_info['min_address']
            max_addr = range_info['max_address']
            
            if min_addr == max_addr:
                range_str = str(min_addr)
            else:
                range_str = f"[{min_addr}, {max_addr}]"
            
            print(f"{cell_name:<40} {address_count:<15} {range_str}")
    
    def save_address_lists_to_csv(self, output_path: str):
        """Save cell address lists to a CSV file"""
        if not self.parameters:
            print("No parameters to save.")
            return
        
        cell_addresses = self.get_cells_with_address_lists()
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['cell_name', 'address_count', 'addresses']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for cell_name in sorted(cell_addresses.keys()):
                    addresses = cell_addresses[cell_name]
                    writer.writerow({
                        'cell_name': cell_name,
                        'address_count': len(addresses),
                        'addresses': ', '.join(addresses)
                    })
                    
            print(f"Cell address lists saved to {output_path}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def save_address_ranges_to_csv(self, output_path: str):
        """Save cell address ranges to a CSV file"""
        if not self.parameters:
            print("No parameters to save.")
            return
        
        cell_ranges = self.get_cells_with_address_ranges()
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['cell_name', 'address_count', 'min_address', 'max_address', 'address_range']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for cell_name in sorted(cell_ranges.keys()):
                    range_info = cell_ranges[cell_name]
                    min_addr = range_info['min_address']
                    max_addr = range_info['max_address']
                    
                    if min_addr == max_addr:
                        range_str = str(min_addr)
                    else:
                        range_str = f"[{min_addr}, {max_addr}]"
                    
                    writer.writerow({
                        'cell_name': cell_name,
                        'address_count': range_info['count'],
                        'min_address': min_addr,
                        'max_address': max_addr,
                        'address_range': range_str
                    })
                    
            print(f"Cell address ranges saved to {output_path}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def save_to_xml(self, output_path: str = None, card_type: str = None, version: str = None):
        """Save parsed parameters to an XML metadata file or print to stdout"""
        # Mapping dictionary from cell/parameter patterns to XML metadata types
        param_mapping = {
            # Direct address mappings
            'balanceRegister': {
                'pattern': ('L-R Balance.Balance', 'DCInpAlg145X11value'),
                'comment': 'L-R Balance control'
            },
            'muteInvertRegister': {
                'pattern': ('Soft Mute', 'ExternalGainAlgSlew145X1slew_mode'),
                'comment': 'Soft mute invert control'
            },
            'volumeControlRegister': {
                'pattern': ('MasterVol', 'HWGainADAU145XAlg5target'),
                'comment': 'Master volume control'
            },
            'volumeLimitPiRegister': {
                'pattern': ('VolumeLimitPi', 'HWGainADAU145XAlg6target'),
                'comment': 'Volume limit for Pi input'
            },
            'volumeLimitSPDIFRegister': {
                'pattern': ('VolumeLimitSPDIF', 'HWGainADAU145XAlg7target'),
                'comment': 'Volume limit for SPDIF input'
            },
            'readSPDIFOnRegister': {
                'pattern': ('Input Detection.SPDIF on read', 'ReadBackAlgNewSigma3001Value'),
                'comment': 'Read SPDIF on status'
            },
            'channelSelectARegister': {
                'pattern': ('Channel Select.Ch_A', 'monomuxSigma300ns4index'),
                'comment': 'Channel A selection'
            },
            'channelSelectBRegister': {
                'pattern': ('Channel Select.Ch_B', 'monomuxSigma300ns3index'),
                'comment': 'Channel B selection'
            },
            'channelSelectCRegister': {
                'pattern': ('Channel Select.Ch_C', 'monomuxSigma300ns2index'),
                'comment': 'Channel C selection'
            },
            'channelSelectDRegister': {
                'pattern': ('Channel Select.Ch_D', 'monomuxSigma300ns1index'),
                'comment': 'Channel D selection'
            },
            'invertARegister': {
                'pattern': ('Loudspeaker EQ.Invert_A', 'EQS300Invert4invert'),
                'comment': 'Invert channel A'
            },
            'invertBRegister': {
                'pattern': ('Loudspeaker EQ.Invert_B', 'EQS300Invert3invert'),
                'comment': 'Invert channel B'
            },
            'invertCRegister': {
                'pattern': ('Loudspeaker EQ.Invert_C', 'EQS300Invert2invert'),
                'comment': 'Invert channel C'
            },
            'invertDRegister': {
                'pattern': ('Loudspeaker EQ.Invert_D', 'EQS300Invert1invert'),
                'comment': 'Invert channel D'
            },
            'delayARegister': {
                'pattern': ('Delay_A', 'DelaySigma300Alg1delay'),
                'comment': 'Delay for channel A'
            },
            'delayBRegister': {
                'pattern': ('Delay_B', 'DelaySigma300Alg4delay'),
                'comment': 'Delay for channel B'
            },
            'delayCRegister': {
                'pattern': ('Delay_C', 'DelaySigma300Alg3delay'),
                'comment': 'Delay for channel C'
            },
            'delayDRegister': {
                'pattern': ('Delay_D', 'DelaySigma300Alg2delay'),
                'comment': 'Delay for channel D'
            },
            # Dynamic registers that need to be found in .params (addresses < 10000)
            'readIsDaisyChainSlaveRegister': {
                'search_pattern': 'readIsDaisyChainSlave',
                'comment': 'Read daisy chain slave status - need to find in .params'
            },
            'sensitivitySPDIFRegister': {
                'search_pattern': 'sensitivitySPDIF',
                'comment': 'SPDIF sensitivity - need to find in .params'
            },
            'enableSPDIFRegister': {
                'search_pattern': 'enableSPDIF',
                'comment': 'Enable SPDIF - need to find in .params'
            },
            'tuningForkPitchRegister': {
                'search_pattern': 'tuningForkPitch',
                'comment': 'Tuning fork pitch - need to find in .params'
            },
            'tuningForkOnRegister': {
                'search_pattern': 'tuningForkOn',
                'comment': 'Tuning fork on - need to find in .params'
            },
            # Filter bank mappings (startaddress/length format)
            'IIR_A': {
                'cell_name': 'Loudspeaker EQ.IIR_A',
                'filter_bank': True,
                'comment': 'IIR filter bank for channel A'
            },
            'IIR_B': {
                'cell_name': 'Loudspeaker EQ.IIR_B',
                'filter_bank': True,
                'comment': 'IIR filter bank for channel B'
            },
            'IIR_C': {
                'cell_name': 'Loudspeaker EQ.IIR_C',
                'filter_bank': True,
                'comment': 'IIR filter bank for channel C'
            },
            'IIR_D': {
                'cell_name': 'Loudspeaker EQ.IIR_D',
                'filter_bank': True,
                'comment': 'IIR filter bank for channel D'
            },
            'toneControlLeftRegisters': {
                'cell_name': 'Tone Controls.ToneControl_L',
                'filter_bank': True,
                'comment': 'Tone control filter bank for left channel'
            },
            'toneControlRightRegisters': {
                'cell_name': 'Tone Controls.ToneControl_R',
                'filter_bank': True,
                'comment': 'Tone control filter bank for right channel'
            },
            'customFilterRegisterBankLeft': {
                'cell_name': 'Room Compensation.IIR_L',
                'filter_bank': True,
                'comment': 'Custom filter bank for left channel (room compensation)'
            },
            'customFilterRegisterBankRight': {
                'cell_name': 'Room Compensation.IIR_R',
                'filter_bank': True,
                'comment': 'Custom filter bank for right channel (room compensation)'
            },
            # Level registers - need to find specific target parameters
            'levelsARegister': {
                'cell_pattern': 'Levels',
                'param_pattern': 'HWGainADAU145XAlg.*target',
                'channel': 'A',
                'comment': 'Level control for channel A - need to identify specific parameter'
            },
            'levelsBRegister': {
                'cell_pattern': 'Levels', 
                'param_pattern': 'HWGainADAU145XAlg.*target',
                'channel': 'B',
                'comment': 'Level control for channel B - need to identify specific parameter'
            },
            'levelsCRegister': {
                'cell_pattern': 'Levels',
                'param_pattern': 'HWGainADAU145XAlg.*target', 
                'channel': 'C',
                'comment': 'Level control for channel C - need to identify specific parameter'
            },
            'levelsDRegister': {
                'cell_pattern': 'Levels',
                'param_pattern': 'HWGainADAU145XAlg.*target',
                'channel': 'D', 
                'comment': 'Level control for channel D - need to identify specific parameter'
            }
        }
        
        # Create a lookup table for quick parameter access
        param_lookup = {}
        cell_ranges = self.get_cells_with_address_ranges()
        
        for param in self.parameters:
            key = (param['cell_name'], param['parameter_name'])
            param_lookup[key] = param['parameter_address']
        
        # Helper function to find parameter address
        def get_param_address(xml_type, mapping_info):
            if 'pattern' in mapping_info:
                cell_name, param_name = mapping_info['pattern']
                return param_lookup.get((cell_name, param_name))
            elif 'filter_bank' in mapping_info:
                cell_name = mapping_info['cell_name']
                if cell_name in cell_ranges:
                    range_info = cell_ranges[cell_name]
                    start_addr = range_info['min_address']
                    count = range_info['count']
                    return f"{start_addr}/{count}"
            elif 'search_pattern' in mapping_info:
                # Search for parameters that might match the pattern
                search_pattern = mapping_info['search_pattern'].lower()
                for param in self.parameters:
                    cell_name = param['cell_name'].lower()
                    param_name = param['parameter_name'].lower()
                    if search_pattern in cell_name or search_pattern in param_name:
                        # Found a potential match, but we need better logic here
                        # For now, return None to indicate it needs manual mapping
                        pass
                return None  # TODO: Implement better search logic
            elif 'cell_pattern' in mapping_info:
                # For level registers, try to find the right parameter
                # This is a placeholder - would need more analysis to map correctly
                return "UNKNOWN"  # TODO: Map level registers properly
            return None
        
        # Build the XML content with actual parameter values
        # Define card-specific metadata
        card_metadata = {
            'beocreate': {
                'profileName': 'Beocreate Universal',
                'programID': 'beocreate-universal',
                'modelName': 'Beocreate 4-Channel Amplifier',
                'modelID': 'beocreate-4ca-mk1',
                'defaultVersion': '11'
            },
            'dacdsp': {
                'profileName': 'DAC+ DSP Universal',
                'programID': 'dacdsp-universal',
                'modelName': 'DAC+ DSP',
                'modelID': 'hifiberry-dacdsp',
                'defaultVersion': '15'
            },
            'dspaddon': {
                'profileName': 'DSP add-on',
                'programID': 'dsp-addon',
                'modelName': 'DSP add-on',
                'modelID': 'dsp-addon',
                'defaultVersion': '14'
            }
        }
        
        # Use provided card type or default to generic values
        if card_type and card_type in card_metadata:
            metadata = card_metadata[card_type]
            profile_name = metadata['profileName']
            program_id = metadata['programID']
            model_name = metadata['modelName']
            model_id = metadata['modelID']
            profile_version = version or metadata['defaultVersion']
        else:
            # Generic defaults when card type not specified
            profile_name = 'NAME'
            program_id = 'NAME'
            model_name = 'NAME'
            model_id = 'NAME'
            profile_version = version or '0'
        
        xml_lines = [
            '                <metadata type="sampleRate">48000</metadata>',
            f'                <metadata type="profileName">{profile_name}</metadata>',
            f'                <metadata type="profileVersion">{profile_version}</metadata>',
            f'                <metadata type="programID">{program_id}</metadata>',
            f'                <metadata type="modelName" modelID="{model_id}">{model_name}</metadata>',
            '                <metadata type="checksum">CHECKSUM</metadata>',
            '                <metadata type="spdifTXUserDataSource" storable="yes">63135</metadata>',
            '                <metadata type="spdifTXUserDataL0" storable="yes">63135</metadata>',
            '                <metadata type="spdifTXUserDataL1" storable="yes">63168</metadata>',
            '                <metadata type="spdifTXUserDataL2" storable="yes">63169</metadata>',
            '                <metadata type="spdifTXUserDataL3" storable="yes">63170</metadata>',
            '                <metadata type="spdifTXUserDataL4" storable="yes">63171</metadata>',
            '                <metadata type="spdifTXUserDataL5" storable="yes">63172</metadata>',
            '                <metadata type="spdifTXUserDataR0" storable="yes">63173</metadata>',
            '                <metadata type="spdifTXUserDataR1" storable="yes">63185</metadata>',
            '                <!-- DSP parameters from .params file -->'
        ]
        
        # Add parameters that don't have direct mappings (static values for addresses >= 10000 only)
        static_params = [
            ('canBecomeDaisyChainSlaveRegister', '4833'),  # This should be found in .params if < 10000
            ('muteRegister', '4834'),  # This should be found in .params if < 10000
            ('enableSPDIFTransmitterRegister', '4835'),  # This should be found in .params if < 10000
            ('disableSPDIFTransmitterAtMuteRegister', '4836'),  # This should be found in .params if < 10000
            # Only include addresses >= 10000 as truly static
            # Addresses < 10000 should come from .params file
        ]
        
        for param_info in static_params:
            param_type = param_info[0]
            param_value = param_info[1]
            extra_attrs = param_info[2] if len(param_info) > 2 else ''
            if extra_attrs:
                xml_lines.append(f'                <metadata type="{param_type}" {extra_attrs}>{param_value}</metadata>')
            else:
                xml_lines.append(f'                <metadata type="{param_type}">{param_value}</metadata>')
        
        # Add mapped parameters from .params file
        for xml_type, mapping_info in param_mapping.items():
            address = get_param_address(xml_type, mapping_info)
            if address is not None:
                # Determine attributes based on parameter type
                if xml_type.startswith('channelSelect'):
                    attrs = 'channels="left,right,mono,side" multiplier="1" storable="yes"'
                elif xml_type.startswith('delay'):
                    attrs = 'maxDelay="2000" storable="yes"'
                elif xml_type in ['volumeControlRegister', 'volumeLimitPiRegister', 'volumeLimitSPDIFRegister', 
                                 'balanceRegister', 'muteInvertRegister', 'enableSPDIFRegister'] or xml_type.startswith('invert') or xml_type.startswith('levels') or 'Filter' in xml_type or xml_type.startswith('IIR_') or 'toneControl' in xml_type:
                    attrs = 'storable="yes"'
                else:
                    attrs = ''
                
                if attrs:
                    xml_lines.append(f'                <metadata type="{xml_type}" {attrs}>{address}</metadata>')
                else:
                    xml_lines.append(f'                <metadata type="{xml_type}">{address}</metadata>')
            else:
                # Add comment for unmapped parameters
                xml_lines.append(f'                <!-- {xml_type}: {mapping_info["comment"]} - NOT MAPPED -->')
        
        xml_content = '\n'.join(xml_lines)
        
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as xmlfile:
                    xmlfile.write(xml_content)
                        
                print(f"XML metadata saved to {output_path}")
                
            except Exception as e:
                print(f"Error saving to XML: {e}")
        else:
            # Print to stdout
            print(xml_content)
    
    def save_to_csv(self, output_path: str):
        """Save parsed parameters to a CSV file"""
        if not self.parameters:
            print("No parameters to save.")
            return
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['cell_name', 'parameter_name', 'parameter_address']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for param in self.parameters:
                    writer.writerow(param)
                    
            print(f"Parameters saved to {output_path}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def get_parameters_by_cell(self, cell_name: str) -> List[Dict[str, str]]:
        """Get all parameters for a specific cell"""
        return [param for param in self.parameters if param['cell_name'] == cell_name]
    
    def get_unique_cells(self) -> List[str]:
        """Get list of unique cell names"""
        return list(set(param['cell_name'] for param in self.parameters))
    
    def get_cells_with_address_lists(self) -> Dict[str, List[str]]:
        """Get dictionary mapping cell names to lists of their parameter addresses"""
        cell_addresses = {}
        
        for param in self.parameters:
            cell_name = param['cell_name']
            address = param['parameter_address']
            
            if cell_name not in cell_addresses:
                cell_addresses[cell_name] = []
            
            if address not in cell_addresses[cell_name]:
                cell_addresses[cell_name].append(address)
        
        # Sort addresses numerically for each cell
        for cell_name in cell_addresses:
            cell_addresses[cell_name].sort(key=int)
        
        return cell_addresses
    
    def get_cells_with_address_ranges(self) -> Dict[str, Dict[str, any]]:
        """Get dictionary mapping cell names to their address ranges and counts"""
        cell_ranges = {}
        
        for param in self.parameters:
            cell_name = param['cell_name']
            address = int(param['parameter_address'])
            
            if cell_name not in cell_ranges:
                cell_ranges[cell_name] = {
                    'min_address': address,
                    'max_address': address,
                    'count': 1,
                    'addresses': set([address])
                }
            else:
                cell_ranges[cell_name]['addresses'].add(address)
                cell_ranges[cell_name]['min_address'] = min(cell_ranges[cell_name]['min_address'], address)
                cell_ranges[cell_name]['max_address'] = max(cell_ranges[cell_name]['max_address'], address)
                cell_ranges[cell_name]['count'] = len(cell_ranges[cell_name]['addresses'])
        
        return cell_ranges


def main():
    """Main function to handle command line arguments and run the parser"""
    parser = argparse.ArgumentParser(description='Parse DSP .params files')
    parser.add_argument('input_file', help='Path to the .params file to parse')
    parser.add_argument('--output', '-o', help='Output CSV file path (optional)')
    parser.add_argument('--cell', '-c', help='Filter by specific cell name (optional)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress console output')
    parser.add_argument('--address-lists', action='store_true', 
                       help='Group parameters by cell and show address lists instead of individual parameters')
    parser.add_argument('--address-range', action='store_true',
                       help='Group parameters by cell and show address ranges [min, max] instead of individual parameters')
    parser.add_argument('--xml', action='store_true',
                       help='Output XML metadata format instead of CSV')
    parser.add_argument('--card', choices=['beocreate', 'dacdsp', 'dspaddon'], 
                       help='Card type for XML metadata generation (beocreate, dacdsp, dspaddon)')
    parser.add_argument('--version', help='Version number for the profile')
    
    args = parser.parse_args()
    
    # Check for conflicting arguments
    if args.address_lists and args.address_range:
        print("Error: Cannot use both --address-lists and --address-range at the same time.")
        return
    
    # Create parser instance and parse the file
    dsp_parser = DSPParamsParser()
    parameters = dsp_parser.parse_file(args.input_file)
    
    if not parameters:
        print("No parameters found in the file.")
        return
    
    print(f"Successfully parsed {len(parameters)} parameters from {args.input_file}")
    
    # Handle XML output
    if args.xml:
        dsp_parser.save_to_xml(args.output, args.card, args.version)
        if not args.quiet and args.output:
            print(f"\nXML metadata generated and saved to {args.output}")
        return
    
    # Handle address range mode
    if args.address_range:
        cell_ranges = dsp_parser.get_cells_with_address_ranges()
        
        if args.cell:
            # Filter by specific cell
            if args.cell in cell_ranges:
                print(f"\nAddress range for cell '{args.cell}':")
                range_info = cell_ranges[args.cell]
                min_addr = range_info['min_address']
                max_addr = range_info['max_address']
                count = range_info['count']
                
                if min_addr == max_addr:
                    range_str = str(min_addr)
                else:
                    range_str = f"[{min_addr}, {max_addr}]"
                
                print(f"Address count: {count}")
                print(f"Address range: {range_str}")
            else:
                print(f"Cell '{args.cell}' not found")
                print("Available cells:")
                for cell in sorted(cell_ranges.keys()):
                    print(f"  - {cell}")
        elif not args.quiet:
            # Show all cells with address ranges
            print("\nCells with address ranges:")
            dsp_parser.print_address_ranges()
        
        # Save to CSV if requested (address ranges format)
        if args.output:
            if args.cell and args.cell in cell_ranges:
                # Save single cell to CSV
                temp_parser = DSPParamsParser()
                temp_parser.parameters = dsp_parser.get_parameters_by_cell(args.cell)
                temp_parser.save_address_ranges_to_csv(args.output)
            else:
                # Save all cells to CSV
                dsp_parser.save_address_ranges_to_csv(args.output)
        
        # Print summary for address ranges mode
        if not args.quiet:
            print(f"\nSummary:")
            print(f"Total parameters: {len(parameters)}")
            print(f"Unique cells: {len(cell_ranges)}")
            total_addresses = sum(range_info['count'] for range_info in cell_ranges.values())
            print(f"Unique addresses: {total_addresses}")
    
    # Handle address lists mode
    elif args.address_lists:
        cell_addresses = dsp_parser.get_cells_with_address_lists()
        
        if args.cell:
            # Filter by specific cell
            if args.cell in cell_addresses:
                print(f"\nAddress list for cell '{args.cell}':")
                addresses = cell_addresses[args.cell]
                print(f"Address count: {len(addresses)}")
                print(f"Addresses: {', '.join(addresses)}")
            else:
                print(f"Cell '{args.cell}' not found")
                print("Available cells:")
                for cell in sorted(cell_addresses.keys()):
                    print(f"  - {cell}")
        elif not args.quiet:
            # Show all cells with address lists
            print("\nCells with address lists:")
            dsp_parser.print_address_lists()
        
        # Save to CSV if requested (address lists format)
        if args.output:
            if args.cell and args.cell in cell_addresses:
                # Save single cell to CSV
                temp_parser = DSPParamsParser()
                temp_parser.parameters = dsp_parser.get_parameters_by_cell(args.cell)
                temp_parser.save_address_lists_to_csv(args.output)
            else:
                # Save all cells to CSV
                dsp_parser.save_address_lists_to_csv(args.output)
        
        # Print summary for address lists mode
        if not args.quiet:
            print(f"\nSummary:")
            print(f"Total parameters: {len(parameters)}")
            print(f"Unique cells: {len(cell_addresses)}")
            total_addresses = sum(len(addrs) for addrs in cell_addresses.values())
            print(f"Unique addresses: {total_addresses}")
    
    else:
        # Original mode - individual parameters
        # Filter by cell if requested
        if args.cell:
            filtered_params = dsp_parser.get_parameters_by_cell(args.cell)
            if filtered_params:
                print(f"\nParameters for cell '{args.cell}':")
                temp_parser = DSPParamsParser()
                temp_parser.parameters = filtered_params
                temp_parser.print_parameters()
            else:
                print(f"No parameters found for cell '{args.cell}'")
                print("Available cells:")
                for cell in dsp_parser.get_unique_cells():
                    print(f"  - {cell}")
        elif not args.quiet:
            # Print all parameters
            print("\nAll parameters:")
            dsp_parser.print_parameters()
        
        # Save to CSV if requested (individual parameters format)
        if args.output:
            if args.cell:
                temp_parser = DSPParamsParser()
                temp_parser.parameters = dsp_parser.get_parameters_by_cell(args.cell)
                temp_parser.save_to_csv(args.output)
            else:
                dsp_parser.save_to_csv(args.output)
        
        # Print summary for individual parameters mode
        if not args.quiet:
            print(f"\nSummary:")
            print(f"Total parameters: {len(parameters)}")
            print(f"Unique cells: {len(dsp_parser.get_unique_cells())}")


if __name__ == "__main__":
    main()
