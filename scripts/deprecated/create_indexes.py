import mongolia
from pymongo import ASCENDING, HASHED, DESCENDING

base = mongolia.mongo_connection.CONNECTION.get_connection()['beiwe']
chunk_registry = base.get_collection("chunk_registry")
uploads = base.get_collection("upload_tracking")

# So, hash type indexes don't go fast?  probably because most of these fields are unique, so the hash table is not actually an improvement
# REMOVING the hash index sped up ChunksRegistry(chunk_path= u'CHUNKED_DATA/56d0b84e1206f706e258de83/h63bb8lf/wifi/2016-11-30T11:00:00.csv')
# from 1.5 to 1.2, making the index Ascending brought it to 351 micro seconds.

print "generating indexes for chunk_registry..."
print "indexing study_id..."
chunk_registry.create_index([('study_id', ASCENDING)], background=True)

print "indexing data_type..."
chunk_registry.create_index([('data_type', ASCENDING)], background=True)

print "indexing user_id..."
chunk_registry.create_index([('user_id', ASCENDING)], background=True)

print "indexing survey_id..."
chunk_registry.create_index([('survey_id', ASCENDING)], background=True)

print "indexing time_bin..."
chunk_registry.create_index([('time_bin', ASCENDING)], background=True)

print "indexing chunk_path..."
chunk_registry.create_index([('chunk_path', ASCENDING)], background=True)

print "generating index for uploads..."
print "generating index for timestamp..."
uploads.create_index([('timestamp', ASCENDING)], background=True)

print "generating index for user_id..."
uploads.create_index([('user_id', ASCENDING)], background=True)

print "generating index for file_path..."
uploads.create_index([('file_path', ASCENDING)], background=True)

print "these indexes exist"
indexes = [index.to_dict()['key'].items()[0] for index in chunk_registry.list_indexes()]
for name, index_type in indexes:
    index_type = "ascending" if index_type is 1 else index_type
    index_type = "descending" if index_type is -1 else index_type
    print name, ":", index_type.upper()

indexes = [index.to_dict()['key'].items()[0] for index in uploads.list_indexes()]
for name, index_type in indexes:
    index_type = "ascending" if index_type is 1 else index_type
    index_type = "descending" if index_type is -1 else index_type
    print name, ":", index_type.upper()
