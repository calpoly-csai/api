#!/usr/bin/env python3
from database_wrapper import NimbusMySQL

if __name__ == "__main__":
    db = NimbusMySQL(config_file="config.json")

    ents = db.get_entities()

    print("Entites:", ents)

    uniq_depts = db.get_unique(entity="Courses", prop="dept")

    print("Unique departments?:", uniq_depts)

    bitcounts = db.get_bitcount(entity="Courses", prop="termsOffered")

    print("How many terms is CSC 100 offered?:", bitcounts[0])
