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
    
    def save_to_xml(self, output_path: str):
        """Save parsed parameters to an XML metadata file"""
        xml_content = '''                
                <metadata type="sampleRate">48000</metadata>
                <metadata type="profileName">NAME</metadata>
                <metadata type="profileVersion">0</metadata>
                <metadata type="programID">NAME</metadata>
                <metadata type="modelName" modelID="NAME">NAME</metadata>
                <metadata type="checksum">CHECKSUM</metadata>
                <metadata type="spdifTXUserDataSource" storable="yes">63135</metadata>
                <metadata type="spdifTXUserDataL0" storable="yes">63135</metadata>
                <metadata type="spdifTXUserDataL1" storable="yes">63168</metadata>
                <metadata type="spdifTXUserDataL2" storable="yes">63169</metadata>
                <metadata type="spdifTXUserDataL3" storable="yes">63170</metadata>
                <metadata type="spdifTXUserDataL4" storable="yes">63171</metadata>
                <metadata type="spdifTXUserDataL5" storable="yes">63172</metadata>
                <metadata type="spdifTXUserDataR0" storable="yes">63173</metadata>
                <metadata type="spdifTXUserDataR1" storable="yes">63185</metadata>
                <!-- Additional metadata entries -->
                <metadata type="readIsDaisyChainSlaveRegister">98</metadata>
                <metadata type="canBecomeDaisyChainSlaveRegister">4833</metadata>
                <metadata type="muteRegister">4834</metadata>
                <metadata type="muteInvertRegister" storable="yes">4856</metadata>
                <metadata type="enableSPDIFTransmitterRegister">4835</metadata>
                <metadata type="disableSPDIFTransmitterAtMuteRegister">4836</metadata>
                <metadata type="sensitivitySPDIFRegister">86</metadata>
                <metadata type="enableSPDIFRegister" storable="yes">4841</metadata>
                <metadata type="readSPDIFOnRegister">93</metadata>
                <metadata type="tuningForkPitchRegister">29</metadata>
                <metadata type="tuningForkOnRegister">25</metadata>
                <metadata type="customFilterRegisterBankLeft" storable="yes">329/80</metadata>
                <metadata type="customFilterRegisterBankRight" storable="yes">249/80</metadata>
                <metadata type="toneControlRightRegisters" storable="yes">108/70</metadata>
                <metadata type="toneControlLeftRegisters" storable="yes">179/70</metadata>
                <metadata type="channelSelectDRegister" channels="left,right,mono,side" multiplier="1" storable="yes">4860</metadata>
                <metadata type="channelSelectCRegister" channels="left,right,mono,side" multiplier="1" storable="yes">4863</metadata>
                <metadata type="channelSelectBRegister" channels="left,right,mono,side" multiplier="1" storable="yes">4862</metadata>
                <metadata type="channelSelectARegister" channels="left,right,mono,side" multiplier="1" storable="yes">4861</metadata>
                <metadata type="invertDRegister" storable="yes">4864</metadata>
                <metadata type="invertCRegister" storable="yes">4865</metadata>
                <metadata type="invertBRegister" storable="yes">4866</metadata>
                <metadata type="invertARegister" storable="yes">4867</metadata>
                <metadata type="IIR_D" storable="yes">451/80</metadata>
                <metadata type="IIR_C" storable="yes">531/80</metadata>
                <metadata type="IIR_B" storable="yes">611/80</metadata>
                <metadata type="IIR_A" storable="yes">691/80</metadata>
                <metadata type="levelsARegister" storable="yes">781</metadata>
                <metadata type="levelsBRegister" storable="yes">778</metadata>
                <metadata type="levelsCRegister" storable="yes">775</metadata>
                <metadata type="levelsDRegister" storable="yes">772</metadata>
                <metadata type="volumeControlRegister" storable="yes">106</metadata>
                <metadata type="volumeLimitRegister">74</metadata>
                <metadata type="volumeLimitPiRegister" storable="yes">74</metadata>
                <metadata type="volumeLimitSPDIFRegister" storable="yes">77</metadata>
                <metadata type="delayARegister" maxDelay="2000" storable="yes">786</metadata>
                <metadata type="delayDRegister" maxDelay="2000" storable="yes">783</metadata>
                <metadata type="delayCRegister" maxDelay="2000" storable="yes">784</metadata>
                <metadata type="delayBRegister" maxDelay="2000" storable="yes">785</metadata>'''
        
        try:
            with open(output_path, 'w', encoding='utf-8') as xmlfile:
                xmlfile.write(xml_content)
                    
            print(f"XML metadata saved to {output_path}")
            
        except Exception as e:
            print(f"Error saving to XML: {e}")
    
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
                       help='Output XML metadata format instead of CSV (requires --output)')
    
    args = parser.parse_args()
    
    # Check for conflicting arguments
    if args.address_lists and args.address_range:
        print("Error: Cannot use both --address-lists and --address-range at the same time.")
        return
    
    if args.xml and not args.output:
        print("Error: --xml option requires --output to specify the output file.")
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
        dsp_parser.save_to_xml(args.output)
        if not args.quiet:
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
