# Worm-Tagging

**Centroid**: TODO

**Worm**: TODO

**Superdoc**: Each worm has a corresponding superdoc, indexed by
  `worm_id`, and composed of the concatenation of a sampling of
  `patent_text`s from the worm's centroid's patents' text.
- worms with 2 or less centroids are omitted from superdoc creation.
- superdocs use a sampling of 50 `patent_text`s


**TF-IDF**: TODO
