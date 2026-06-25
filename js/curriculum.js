/**
 * NEET Biology curriculum — Class XI / XII chapter architecture.
 * Maps bank `topic` values to a stable syllabus tree; subtopics = question sections.
 */
(function (global) {
  const CHAPTER_ALIASES = {};

  const SECTION_TYPES = [
    { key: 'level1', label: 'Level I', icon: '📝' },
    { key: 'level2', label: 'Level II', icon: '🔬' },
    { key: 'pyq', label: 'Previous Years NEET', icon: '🎯' },
    { key: 'reneet2026', label: 'reNEET 2026', icon: '🎓' }
  ];

  const CURRICULUM = [
    {
      id: 'xi',
      label: 'Class XI',
      subtitle: 'Botany & Zoology — Part 1',
      units: [
        {
          id: 'xi-diversity',
          label: 'Diversity in the Living World',
          chapters: [
            'Living World',
            'Biological Classification',
            'Plant Kingdom',
            'Animal Classification'
          ]
        },
        {
          id: 'xi-structural',
          label: 'Structural Organisation in Plants & Animals',
          chapters: [
            'Plant Morphology',
            'Anatomy of Flowering Plants',
            'Structural Organization in Animals'
          ]
        },
        {
          id: 'xi-cell',
          label: 'Cell Structure & Function',
          chapters: [
            'Cell: The Unit of Life',
            'Biomolecules',
            'Cell Cycle and Cell Division'
          ]
        },
        {
          id: 'xi-plant-physiology',
          label: 'Plant Physiology',
          chapters: [
            'Transport in Plants',
            'Mineral Nutrition',
            'Photosynthesis in Higher Plants',
            'Respiration in Plants',
            'Plant Growth and Development'
          ]
        },
        {
          id: 'xi-human-physiology',
          label: 'Human Physiology',
          chapters: [
            'Digestion and Absorption',
            'Breathing and Exchange of Gases',
            'Body Fluids and Circulation',
            'Products and Their Elimination',
            'Locomotion and Movement',
            'Neural Control and Co-ordination',
            'Co-ordination and Integration'
          ]
        }
      ]
    },
    {
      id: 'xii',
      label: 'Class XII',
      subtitle: 'Botany & Zoology — Part 2',
      units: [
        {
          id: 'xii-reproduction',
          label: 'Reproduction',
          chapters: [
            'Reproduction in Organisms',
            'Reproduction in Flowering Plant',
            'Human Reproduction',
            'Reproductive Health'
          ]
        },
        {
          id: 'xii-genetics',
          label: 'Genetics & Evolution',
          chapters: [
            'Principles of Inheritance and Variation',
            'Molecular Basis of Inheritance',
            'Evolution'
          ]
        },
        {
          id: 'xii-welfare',
          label: 'Biology in Human Welfare',
          chapters: [
            'Human Health and Disease',
            'Strategies for Enhancement in Food Production',
            'Microbes in Human Welfare'
          ]
        },
        {
          id: 'xii-biotech',
          label: 'Biotechnology',
          chapters: [
            'Biotechnology Principles and Processes',
            'Biotechnology and Its Application'
          ]
        },
        {
          id: 'xii-ecology',
          label: 'Ecology',
          chapters: [
            'Organisms and Populations',
            'Ecosystem',
            'Biodiversity and Conservation',
            'Environmental Issues'
          ]
        },
        {
          id: 'xii-reneet',
          label: 'NEET 2026 Re-Examination',
          chapters: [
            'NEET 2026 Re-Exam'
          ]
        }
      ]
    }
  ];

  function normalizeChapter(topic) {
    const value = (topic || '').trim();
    return CHAPTER_ALIASES[value] || value;
  }

  function normalizeSection(subtopic) {
    const raw = (subtopic || '').trim().toLowerCase();
    if (raw === 'level i' || raw === 'level 1') return 'level1';
    if (raw === 'level ii' || raw === 'level 2') return 'level2';
    if (raw.includes('previous') || raw === 'pyq') return 'pyq';
    if (raw.includes('reneet') || raw.includes('re-neet') || raw.includes('re neet')) return 'reneet2026';
    return 'other';
  }

  function sectionLabel(sectionKey) {
    const match = SECTION_TYPES.find(item => item.key === sectionKey);
    return match ? match.label : 'Other';
  }

  function buildQuestionIndex(questions) {
    const byChapter = new Map();

    questions.forEach(question => {
      const chapter = normalizeChapter(question.topic);
      if (!byChapter.has(chapter)) {
        byChapter.set(chapter, { total: 0, sections: new Map(), questions: [] });
      }
      const bucket = byChapter.get(chapter);
      bucket.total += 1;
      bucket.questions.push(question);

      const section = normalizeSection(question.subtopic);
      bucket.sections.set(section, (bucket.sections.get(section) || 0) + 1);
    });

    return byChapter;
  }

  function buildCurriculumTree(questions, getStatus) {
    const index = buildQuestionIndex(questions);

    return CURRICULUM.map(year => ({
      ...year,
      units: year.units.map(unit => ({
        ...unit,
        chapters: unit.chapters.map(chapterName => {
          const bucket = index.get(chapterName) || { total: 0, sections: new Map(), questions: [] };
          let mastered = 0;
          let attempted = 0;
          let wrong = 0;
          let unsolved = 0;

          bucket.questions.forEach(q => {
            const status = getStatus(q.id);
            if (status === 'unsolved') unsolved += 1;
            else attempted += 1;
            if (status === 'mastered') mastered += 1;
            if (status === 'wrong') wrong += 1;
          });

          const sections = SECTION_TYPES.map(type => ({
            ...type,
            count: bucket.sections.get(type.key) || 0,
            questions: bucket.questions.filter(q => normalizeSection(q.subtopic) === type.key)
          })).filter(s => s.count > 0);

          const otherCount = bucket.sections.get('other') || 0;
          if (otherCount) {
            sections.push({
              key: 'other',
              label: 'Mixed',
              icon: '🧬',
              count: otherCount,
              questions: bucket.questions.filter(q => normalizeSection(q.subtopic) === 'other')
            });
          }

          const coverage = bucket.total ? Math.round((mastered / bucket.total) * 100) : 0;
          const progress = bucket.total ? Math.round((attempted / bucket.total) * 100) : 0;

          return {
            id: chapterName,
            name: chapterName,
            total: bucket.total,
            attempted,
            mastered,
            wrong,
            unsolved,
            coverage,
            progress,
            sections,
            inBank: bucket.total > 0
          };
        })
      }))
    }));
  }

  function findChapter(tree, chapterName) {
    const normalized = normalizeChapter(chapterName);
    for (const year of tree) {
      for (const unit of year.units) {
        const chapter = unit.chapters.find(item => item.name === normalized);
        if (chapter) return { year, unit, chapter };
      }
    }
    return null;
  }

  global.NeetCurriculum = {
    CURRICULUM,
    SECTION_TYPES,
    normalizeChapter,
    normalizeSection,
    sectionLabel,
    buildQuestionIndex,
    buildCurriculumTree,
    findChapter
  };
})(window);
