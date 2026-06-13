import argparse
import json
import os
import re
import csv
import sys

def analyze_logs(logs_dir, output_file):
    results = {}
    pattern = re.compile(r'task(\d+).*?cost=\s*(\d+).*?score=\s*([\d\.]+)')
    
    if not os.path.exists(logs_dir):
        print(f"Error: Logs directory not found at {logs_dir}", file=sys.stderr)
        sys.exit(1)
        
    for filename in os.listdir(logs_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(logs_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                matches = pattern.findall(content)
                if matches:
                    results[filename] = [{"task_id": m[0], "cost": int(m[1]), "score": float(m[2])} for m in matches]
                    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Success! Data written to: {output_file}")

def correlate_trace(trace_csv, score_data_file, output_file):
    if not os.path.exists(score_data_file):
        print(f"Error: Score data file not found at {score_data_file}", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(trace_csv):
        print(f"Error: Trace CSV file not found at {trace_csv}", file=sys.stderr)
        sys.exit(1)
        
    with open(score_data_file, 'r') as f:
        score_data = json.load(f)
        
    correlations = []
    with open(trace_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'estimated_improvement' in row and row['estimated_improvement'] != '0.0':
                correlations.append({
                    "step": row["step"],
                    "op": row["op"],
                    "task_id": row["task_id"],
                    "estimated_improvement": row["estimated_improvement"]
                })
                
    with open(output_file, 'w') as f:
        json.dump({"correlations": correlations, "score_data_summary": f"Found {len(score_data)} logs with score data."}, f, indent=2)
    print(f"Success! Data written to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Trace Language Reviewer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    parser_analyze = subparsers.add_parser("analyze-logs")
    parser_analyze.add_argument("--logs-dir", required=True)
    parser_analyze.add_argument("--output", required=True)
    
    parser_correlate = subparsers.add_parser("correlate-trace")
    parser_correlate.add_argument("--trace-csv", required=True)
    parser_correlate.add_argument("--score-data", required=True)
    parser_correlate.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    if args.command == "analyze-logs":
        analyze_logs(args.logs_dir, args.output)
    elif args.command == "correlate-trace":
        correlate_trace(args.trace_csv, args.score_data, args.output)

if __name__ == "__main__":
    main()
