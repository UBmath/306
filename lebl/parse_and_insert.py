# 8/6/2019
# Need to distinguish between exercise prequel to be inserted before 50 vs before 150.

# 7/20/2019
# Want to switch to a JSON-based version.
# I think the existing JSONs I'm already building are sufficient to reconstruct the chapter tex files.



# 6/29/2019
# DONE: How to merge additional exercises from additions1 and additions2??
# Perhaps I should read in the JSON file from additions1 and update that,
# rather than trying to parse the withadd1.tex file.
# Before starting this, I've saved the current version with a 2019_06_29 filename.
 
# DONE: Too many files in top-level directory: should have a build folder where all the non-source gets put.
# Maybe simpler to just run this script in a build folder, and look for the source in the parent folder.
# I will have to simply copy down source folders that have no additions yet.
# Simpler just to copy down all source files to the build folder.

# 6/27/2019 This is the first version where I will merge both Jim/Asela's additions1 and my (Python) additions2.

# 6/25/2019 Workng from parse_and_insert_2019_06_25.py, 
# want to make subsections of source text a list of dicts with the name separated out.

# 6/24/19 Latest update has seriously broken it.
# Be sure to save home version from this morning!
# I should be using revision control!

#assert(False)


import glob
import re
from os.path import exists, join, basename
import os
from zipfile import ZipFile
import json

# 7/23/2019 To remove "comments" in the tex file of the form "{\color{red} blah {blah{}} }"

global_substitutions = {'Poincar\`e':"Poincar\\'e"}  # fix typo in Lebl source tex files

ALL = True #False
REMOVE_RED = ALL  # delete text flagged as incorrect
REMOVE_GREEN = ALL # delete text inserted as proofreading comment
BLUE_TO_BLACK = ALL # revert suggested correction to regular text

GREEN_TO_TEAL = ALL#True  # just because green is too bright for me to read easily

def removeblocks(s0,key):
    # This returns a copy of s0 with all chunks of the form {key [balanced-parens expresssion] }
    # Didn't find any built-in or regex way to do this.
    s = str(s0)
    startstring = '{'+key
    lss = len(startstring)
    while startstring in s:
        i = s.index(startstring)
        #print(i)
        level = 1
        for j,c in enumerate( s[i+lss:] ):
            if c == '{': level += 1
            elif c == '}': level -= 1
            if level == 0: break
        #print(s[i:i+lss+j+1])
        while s[i+lss+j+1].isspace() : j += 1  # get rid of trailing whitespace to avoid creating a paragraph-ending blank line 
        s = s[:i] + s[i+lss+j+1:]
    return s

#s = "Hey {\color{red} and {some{} other} {stuff} the matching } bye {\color{red} and {\color{red} and } {some{} other} {stuff} the matching } bye!"
#removeblocks(s,'\color{red}')

# first extract any text files whose name contains the ADDITIONS_STRING
SOURCE_FOLDER = '..'
JSON_FOLDER = 'jsons'
ADDITIONS_STRING = '-addition' # Asela changed it! # '_additions'

# 6/17/2019 Because Asela is using Overleaf, project can only be downloaded as a whole in zip format, not by individual file.
'''
print('Extracting from zip files')
additionfiles = []
for zipname in []:#TEMPORARy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!sorted( glob.glob('ch-*.zip')):
	print(zipname)
	with ZipFile(zipname, 'r') as zipitem:
		zipadditionfiles = [file for file in zipitem.namelist() if file.endswith(ADDITIONS_STRING+'.tex')]
		additionfiles.extend( zipadditionfiles )
		for file in additionfiles:
			zipitem.extract(file)
			print('\t',file,'extracted')
print(additionfiles,'extracted from zip files')
'''

# 6/27/19 I'm going to do download and extraction all manually for now.


addstrings = ['-additions1', '-additions2'] # these are the strings that will looked for before '.tex' in the additions file names
outstrings = ['-withadd1','-withadd2']  # these are the strings that will be inserted before '.tex' in the merged file name 
instrings  = ['',outstrings[0]] # these are the strings that will looked for before '.tex' in the source file names


leblfiles = [item for item in sorted(glob.glob(join(SOURCE_FOLDER,'ch-*.tex'))) if 'add' not in item]
leblfiles.append('../ap-linear-algebra.tex')
leblfiles.append('../ap-laplace-list.tex')
print('Copying Lebl source files')
for i,leblfile in enumerate(leblfiles):
	print(i,'\t',leblfile)
	cmd = 'cp -p ' + leblfile + ' .'
	#print(cmd)
	os.system(cmd)
#quit()
cmd = 'cp -p ' + join(SOURCE_FOLDER,'diffyqssetupUB.sty') + ' .'
os.system(cmd)
cmd = 'cp -p ' + join(SOURCE_FOLDER,'diffyqs_UB.tex') + ' .'
os.system(cmd)

# The following could be made more efficient by checking if modified since last copy (if preserve timestamp)
cmd = 'cp -pr ' + join(SOURCE_FOLDER,'figures/') + ' .'
os.system(cmd)
cmd = 'cp -pr ' + join(SOURCE_FOLDER,'additional_figures/') + ' .'
os.system(cmd)

# now strip off the SOURCE_FOLDER prefix
leblfiles = [basename(leblfile) for leblfile in leblfiles]


print('Copying additions source files')
additionsfilesets = [sorted(glob.glob(join(SOURCE_FOLDER,'ch-*' + addstring +'.tex'))) for addstring in addstrings]
for additionsfileset in additionsfilesets:
	print('---------------------------------------------------')
	for  additionsfile in additionsfileset:
		print('\t',additionsfile)
		cmd = 'cp -p ' + additionsfile + ' .'
		#print(cmd)
		os.system(cmd)
# now strip off the SOURCE_FOLDER prefix
additionsfilesets = [ [basename(additionsfile) for additionsfile in additionsfileset] for additionsfileset in additionsfilesets ]

# the tex files in the source folder may be write-protected.
cmd = 'chmod 755 *.tex'
os.system(cmd)



# now include all addition files, not just the ones that have been extracted from current zip files
#additionfiles = sorted([file for file in glob.glob('ch-*.tex') if ADDITIONS_STRING in file])
#print( len(additionfiles), 'addition files found altogether' )


def all_but_first_line(s):
	return '\n'.join(s.split('\n')[1:])

def getsectionname(section):
	return section.split('}')[0].split('{')[1]

def dice(s,splitstring):
	bits = s.split(splitstring)
	if s.startswith(splitstring):
		return [splitstring+item for item in bits]
	else:
		return [bits[0]] + [splitstring+item for item in bits[1:]]

subsectionlabelnames = set([])

additionfiles = sorted([f for f in glob.glob('ch-*.tex') if 'addition' in f ])


for additionfile in additionfiles:

	# PARSE THE CHAPTER ADDITIONS FILE ##############################################################

	print()
	print()
	print(additionfile+'********************************************************')
	with open( additionfile ) as f:
		additiontext = f.read()

	#with open('temp1.tex','w') as f: f.write(additiontext)

	if REMOVE_RED:    additiontext = removeblocks(additiontext,'\color{red}')             # requested by Brian Hassard 7/23/19

	#with open('temp2.tex','w') as f: f.write(additiontext)
	#quit()
	if REMOVE_GREEN:  
		additiontext = removeblocks(additiontext,'\color{green}')           # requested by Brian Hassard 7/23/19
		additiontext = removeblocks(additiontext,'\color{teal}')           # 8/2/19 because Brian started using teal directly
	if BLUE_TO_BLACK: additiontext = additiontext.replace('\color{blue}','\color{black}') # requested by Brian Hassard 7/23/19
	if GREEN_TO_TEAL: additiontext = additiontext.replace('\color{green}','\color{teal}') # requested by me 7/26/19

	chapter_additions_dict = {} # keys are section names. We don't need to preserve section order here because that will be dictated by the source text.
	parts = additiontext.split('%extra ')[1:]
	print(additionfile,'has',len(parts),'parts:')
	for part in parts:
		print('PART -----------------------------------------------------------------------------------------------')
		parttype = part.split()[0].strip() 
		print('parttype',parttype)
		# previously, we didn't have to split apart the exercises in part. Now we do.
		sectionname = part.split('{')[1].split('}')[0]
		print('sectionname',sectionname)

		if sectionname not in chapter_additions_dict: chapter_additions_dict[sectionname] = {} 
		#continue
		# now build a list of the parts (types: exercise without answer, exercise with answer, material to precede exercises, exercise header )

		#sectionstartre = '\\\\section{' + sectionname + '}'
		#sectionstart = re.search(sectionstartre,chaptersourcetext).start()
		#exercisesstartre = '\\\\subsection{Exercises}'
		#exercisesstart = sectionstart + re.search(exercisesstartre,chaptersourcetext[sectionstart:]).start()

		if parttype == 'material':
			print('\tmaterial for',sectionname)
			if 'additions_at_end_of_section' not in chapter_additions_dict[sectionname]:
				chapter_additions_dict[sectionname]['additions_at_end_of_section'] = []
			part_without_label = '}'.join( part.split('}')[1:] )
			chapter_additions_dict[sectionname]['additions_at_end_of_section'].append(part_without_label.replace('\\end{document}','').replace('\\printanswers',''))
			#chaptersourcetext = chaptersourcetext[:exercisesstart] + \
			#	'%start_insertion\n' + all_but_first_line(part) + '\n%end_insertion\n\n' + \
			#	chaptersourcetext[exercisesstart:]
			#print(chapter_additions_dict[sectionname])
			#quit()

		elif parttype == 'exercises':
			print('\texercises for',sectionname)

			# 8/6/2019 exercise prequel logic:
			# I think it is simpler than I made it.
			# All we have to do is pack the prequel with the exrercise that follows it.
			# That will happen automatically if we ignore it, except ...
			# if the prequel precedes the very first \begin{exercise},
			# in which case the prequel should be prepended to the first exercise

			EXERCISE_START_STRING = '\\begin{exercise}'
			SOLSTARTSTRING = '\exsol{'
			#PREQUELSTRING = '%exercise-prequel' #-delibterately-corrupted' # What happens if we ignore the prequel comment entirely? Doesn't work. 
			PREQUELBEGIN = '%begin-exercise-prequel'
			PREQUELEND   = '%end-exercise-prequel'
			#bits = part.split(EXERCISE_START_STRING)
			#print('BITS[0]:'+bits[0])
			#print(len(bits)-1,'items')
			#exercises = [EXERCISE_START_STRING]*(len(bits)-1)
			#if PREQUELSTRING in bits[0]:
			#	exercises[0] = bits[0][ bits[0].index(PREQUELSTRING):] + EXERCISE_START_STRING
			#
			#for i in range(len(exercises)):
			#	exercises[i] += bits[i+1]
			#exercisestrings = []

			exercises = [ EXERCISE_START_STRING + item for item in part.split(EXERCISE_START_STRING)[1:] ]

			def pulloutprequel(exercise):
				if PREQUELBEGIN not in exercise or PREQUELEND not in exercise: return exercise
				pieces1 = exercise.split(PREQUELBEGIN)
				pieces2 = pieces1[1].split(PREQUELEND)
				prequel = PREQUELBEGIN + pieces2[0] + PREQUELEND
				exercise_without_prequel = pieces1[0] + pieces2[1]
				return prequel + '\n\n' + exercise_without_prequel

			'''
			for exercise in exercises:
				if PREQUELBEGIN in exercise:
					print(exercise)
					print()
					reformatted_exercise = pulloutprequel(exercise)
					print(reformatted_exercise)
					quit()
			'''

			exercises = [pulloutprequel(exercise) for exercise in exercises]

			exercisestrings = [item.replace('\\end{document}','').replace('\\printanswers','') for item in exercises if SOLSTARTSTRING not in item]	
			chapter_additions_dict[sectionname]['exercises_without_answers'] = exercisestrings
						
			exercisestrings = [item.replace('\\end{document}','').replace('\\printanswers','') for item in exercises if SOLSTARTSTRING     in item]
			chapter_additions_dict[sectionname]['exercises_with_answers'] = exercisestrings

			#print( len(exercises_without_solutions), 'without')
			#print( len(exercises_with_solutions   ), 'with')

			# For each of exercises_with_solutions need to separate the solution from the exercise
			#for item in exercises_with_solutions:
			#	print( len(item.split(SOLSTARTSTRING)), 'chunks' )
			#exercises_with_solutions_exercises = [ item.split(SOLSTARTSTRING)[0] for item in exercises_with_solutions]
			#exercises_with_solutions_answers   = [ SOLSTARTSTRING + item.split(SOLSTARTSTRING)[1] for item in exercises_with_solutions]

			#for item in exercises_with_solutions_exercises: print(item)
			#for item in exercises_with_solutions_answers:   print(item)
			#print('!!!!!!!!!!!!')
			#print(exercises_without_solutions)

		# for easier handling later on ...
		if 'exercises_with_answers'    not in chapter_additions_dict[sectionname]: 
			chapter_additions_dict[sectionname]['exercises_with_answers']    = []
		if 'exercises_without_answers' not in chapter_additions_dict[sectionname]: 
			chapter_additions_dict[sectionname]['exercises_without_answers'] = []

	additionfile_jsonname = join( JSON_FOLDER, basename( additionfile + '.json' ) )
	with open(additionfile_jsonname,'w') as f:
		json.dump(chapter_additions_dict,f,indent=3,sort_keys=True) 

	# At this point we have split the additions into the needed parts.
	# Now we have split the the chapter source text into chunks.
	# header, list of sections, footer

	print('Done writing addition file JSONs')
	
#quit()

# PARSE THE CHAPTER SOURCE FILES ##############################################################

chaptersourcefiles = sorted([f for f in glob.glob('ch-*.tex') if 'addition' not in f and 'withadd' not in f])
for i,chaptersourcefile in enumerate( chaptersourcefiles ):
	print(i,chaptersourcefile)


	print('Reading chapter source file')
	with open( chaptersourcefile ) as f:
		chaptersourcetext = f.read()

	for wrong,right in global_substitutions.items():
		chaptersourcetext = chaptersourcetext.replace(wrong,right)

	SECTION_START_STRING = '\section{'
	pieces = chaptersourcetext.split(SECTION_START_STRING)

	chapter = {'header':pieces[0],'sections':[]}

	chaptersourcesections = [SECTION_START_STRING + piece for piece in pieces[1:]]
	# now we have all the sections separately, and we can concatenate them after inserting the additions
	#print(chaptersourcefile)
	for sectiontext in chaptersourcesections:
		#print('\t'+item[:80])
		sectionname = getsectionname(sectiontext)
		chapter['sections'].append({'sectionname':sectionname})

		# Want to split the section text into body, exercises without answers, exercises with answers

		EXERCISES_START_STRING = '\subsection{Exercises}'
		chaptersourcesectionparts = sectiontext.split(EXERCISES_START_STRING)
		if len(chaptersourcesectionparts)==2:
			chapter['sections'][-1]['body'] = chaptersourcesectionparts[0]

			chaptersourcesection_exercises  = EXERCISES_START_STRING + chaptersourcesectionparts[1]
		
			END_OF_SECTION_STRING = '''%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	\sectionnewpage'''

			EXERCISES_WITH_SOLUTIONS_START_STRING = '\setcounter{exercise}{100}'
			if EXERCISES_WITH_SOLUTIONS_START_STRING in chaptersourcesection_exercises:
				# we have some exercises with answers
				chaptersourcesection_exercises_parts = chaptersourcesection_exercises.split(EXERCISES_WITH_SOLUTIONS_START_STRING)
				chapter['sections'][-1]['exercises_without_answers'] = chaptersourcesection_exercises_parts[0]
				chapter['sections'][-1]['exercises_with_answers'   ] = EXERCISES_WITH_SOLUTIONS_START_STRING + chaptersourcesection_exercises_parts[1] 
			else:
				chapter['sections'][-1]['exercises_without_answers'] = chaptersourcesection_exercises
				chapter['sections'][-1]['exercises_with_answers'   ] = ''

		else:
			chapter['sections'][-1]['body'] = chaptersourcesectionparts[0]  # body will be replaced below by fragmented version
			chapter['sections'][-1]['exercises_without_answers'] = ''
			chapter['sections'][-1]['exercises_with_answers'   ] = ''

	##### FURTHER PARSING OF THE CHAPTER BODY

	#print('Delving into',chapter['header'])
	
	for section in chapter['sections']:

		# Want to split the section body into header, subsections, footer

		#print('.'+section['body'][:50].replace('\n',' ') ) #.split('}')[0]) + '}'
		SUBSECTION_START_STRING = '\subsection{'
		bodybits = dice( section['body'], SUBSECTION_START_STRING )

		#for item in bodybits:
		#	print('ITEM')
		#	print(item)
		#
		#quit()

		if not bodybits[0].startswith(SUBSECTION_START_STRING):
			section['header'] = bodybits[0]
			section['subsections'] = bodybits[1:]
		else:
			section['header'] = ''
			section['subsections'] = bodybits

		del section['body']  # we have now stored the body in header and subsections

		if True: #False:
			##### INSERT A LABEL FOR EVERY SUBSECTION

			subsections_with_labels = []
			for subsection in section['subsections']:
				#firstbit,subsectionbody = subsection.split('}')
				subsectionname =  subsection.split('\subsection{')[1].split('}')[0]
				#while( subsectionname in subsectionlabelnames ):
				#	subsectionname += 'x'
				#subsectionlabelnames.add(subsectionname)
				namebit = '\subsection{' + subsectionname + '}'
				subsectionbody = subsection[len(namebit):]
				#print(namebit,'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
				#print(subsectionbody)

				label = '_'.join(subsectionname.lower().split())  # label is just section name with spaces replaced by underscores
				while label in subsectionlabelnames:  # guard against same section name in different chapters
					label += 'x'
				subsectionlabelnames.add(label)
				labelbit = '\label{inserted_label_' + label + ':subsection}'
				#subsections_with_labels.append( namebit + labelbit + subsectionbody )
				subsections_with_labels.append( {'name':subsectionname,'label':label,'body':subsectionbody } )

				#print(section['subsections'])
				#quit()
			section['subsections'] = subsections_with_labels

		#print('SECTION')
		#print( json.dumps(section['subsections'],indent=4) )
	#quit()
	chaptersourcefile_jsonname = join( JSON_FOLDER, basename( chaptersourcefile + '.json' ) )
	with open(chaptersourcefile_jsonname,'w') as f:
		json.dump(chapter,f,indent=3,sort_keys=True) 


	# 6/29/19 Here, instead of merging additions2 into withadd1 sequentially,
	# we can end the loop and start another where we read the JSON files
	# merge the data structures and then write the merged tex.


# NOW WE MERGE ##############################################################

print('\n\n')
print('MERGING EACH CHAPTER\n')

chaptersourcefiles = sorted([f for f in glob.glob('jsons/ch-*.tex.json') if 'addition' not in f and 'withadd' not in f])
for i,chaptersourcefile in enumerate( chaptersourcefiles ):
	print(i,chaptersourcefile)
	suffix_length = len('.tex.json')
	additionspattern = chaptersourcefile[:-suffix_length]+'-additions*.tex.json'
	additionfiles = sorted( glob.glob( additionspattern ) )

	with open(chaptersourcefile) as f:
		chapter = json.load(f)
	a1 = {}
	a2 = None
	for additionfile in additionfiles:
		print('\t',additionfile)
		if   'additions1' in additionfile:
			with open( additionfile ) as f:
				a1 = json.load(f)
		elif 'additions2' in additionfile:
			with open( additionfile ) as f:
				a2 = json.load(f)

	# a1, a2 will be None if there is no corresponding additions file
	#print(a1.keys())
	if not a2 is None:
		# merge a2 into a1
		for sectionname in a2:
			print('\t\t',sectionname)
			if sectionname not in a1:
				# create new section in a1
				print('\t\t\tNo additions1 here',sectionname)
				a1[sectionname] = a2[sectionname]  # this is shallow - so don't mess up a2 until we're done
			else:
				# appending exercises to a1
				print('\t\t\tAppending additions')
				for key in ['additions_at_end_of_section','exercises_without_answers','exercises_with_answers']:
					if key in a2[sectionname] and len(a2[sectionname][key])>0:
						if key in a1[sectionname]:
							print('\t\t\t\tAppending',len(a2[sectionname][key]), key)
							a1[sectionname][key] += a2[sectionname][key]   # may actually be empty list, but that's ok. Have to check because extra material may be absent.
						else:
							print('\t\t\t\tNew',len(a2[sectionname][key]), key)
							a1[sectionname][key] = a2[sectionname][key] # may actually be empty list

	#if 'first-o' in chaptersourcefile:
	#	with open('temp.json','w') as f:
	#		json.dump(a1,f,indent=3,sort_keys=True)
		#quit()

	mergedtext = ''
	mergedtext += chapter['header']
	for section in chapter['sections']:
		sectionname = section['sectionname']

		#print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
		#print(section)

		if sectionname in a1:
			sectionadditions = a1[sectionname]
			#mergedtext += section['body']
			mergedtext += section['header']
			for subsection in section['subsections']:
				namebit = '\subsection{' + subsection['name'] + '}'
				mergedtext += namebit
				labelbit = '\label{inserted_label_' + subsection['label'] + ':subsection}'
				mergedtext += labelbit
				#if 'sectionnewpage' in subsection['body']:
					#print( subsection['body'] )
					#print()
					#print( 'sectionnewpage' in subsection['body'].replace('\sectionnewpage','') )
					#quit()
					#print('wowowow in',chaptersourcefile)
					#mergedtext += 'wowowowowowo\n'
					#quit()
				mergedtext += subsection['body'].replace('\sectionnewpage','')  # we will write it ourselves after the exercises
			if 'additions_at_end_of_section' in sectionadditions:
				for endofsectionaddition in sectionadditions['additions_at_end_of_section']:
					mergedtext += endofsectionaddition.replace('\sectionnewpage','')

			mergedtext += section['exercises_without_answers'].replace('\sectionnewpage','')
			mergedtext += '\n\n\setcounter{exercise}{50}\n\n'
			mergedtext += '\n\n'.join(sectionadditions['exercises_without_answers']).replace('\sectionnewpage','')

			mergedtext += section['exercises_with_answers'].replace('\sectionnewpage','')
			mergedtext += '\n\n\setcounter{exercise}{150}\n\n'
			mergedtext += '\n\n'.join(sectionadditions['exercises_with_answers']).replace('\sectionnewpage','')

		else:
			#mergedtext += section['body']
			mergedtext += section['header']
			for subsection in section['subsections']:
				namebit = '\subsection{' + subsection['name'] + '}'
				mergedtext += namebit
				labelbit = '\label{inserted_label_' + subsection['label'] + ':subsection}'
				mergedtext += labelbit
				mergedtext += subsection['body'].replace('\sectionnewpage','')  # we will write it ourselves after the exercises
			mergedtext += section['exercises_without_answers'].replace('\sectionnewpage','')
			mergedtext += section['exercises_with_answers'].replace('\sectionnewpage','')
		mergedtext += '\sectionnewpage' + '\n\n'

	print('!!!!!!!!!!',chaptersourcefile,'withadds')
	outputfile = basename(chaptersourcefile)[:-suffix_length] + '-withadds.tex'
	print('~~~~~~~~~~',outputfile)

	with open(outputfile,'w') as f:
		f.write(mergedtext)
	
print('\nRunning pdflatex. \nYou may need to hit Enter a few times to get pdflatex to complete.')

print('\n(If it doesn\'t complete, cd into build_folder and run pdflatex directly to see errors.')
# compile everything
cmd = 'pdflatex diffyqs_UB.tex > temp.log'
os.system(cmd)
print('Done.')

