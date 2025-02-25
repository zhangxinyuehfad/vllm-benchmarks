import argparse
from data import data_prc

parser = argparse.ArgumentParser(description='add commit msg to es')

parser.add_argument('--commit_id', type=str, required=True)
parser.add_argument('--commit_title', type=str, required=True)



if __name__ == '__main__':
    args = parser.parse_args()
    main(args.commit_id, args.commit_title)