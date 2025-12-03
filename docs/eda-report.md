
1. Info

Column	             Meaning	                    Good?	            Notes
EC_number	        Functional label for enzyme	    Good	            Must validate format
UniProt_ID	        Unique protein ID	            Good	            Must check regex
Enzyme_name	        Primary enzyme name	            Present	            Mostly descriptive
Alt_names	        Alternative names	            Missing ~47k	    Expected
Reaction	        Catalyzed reaction	            Present	            Useful for text mining later
Prosite_refs	    PROSITE patterns	            ALL NULL	        To be dropped
Sequence	        Amino-acid sequence	            Critical	        Must validate
Length	            Sequence length	                Good	            Must match Sequence
Organism	        Species	                        Good	            For taxonomy effects
Protein_name	    Usually matches UniProt name	Present	            Redundant sometimes
Gene_name	        Gene symbol	                    Missing ~14k	    Expected
emb_idx	            Index pointing to ESM embedding tensor	Critical	Perfect