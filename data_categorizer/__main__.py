import argparse
from .processor import Processor

def main():
    parser = argparse.ArgumentParser(description='Process and categorize survey data')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('output_file', help='Output CSV file path')
    parser.add_argument('model_name', help='Model name (e.g., phi4-mini:latest)')
    
    args = parser.parse_args()
    
    processor = Processor(args.input_file, args.output_file, args.model_name)
    processor.call()

if __name__ == "__main__":
    main()