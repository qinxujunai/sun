const steps = [
  { en: 'THE QUESTION', title: '先弄清楚，<br>你真正想解决什么。', desc: '明确目标、选项、时间和约束。信息不足时，先提出假设，或者问一个关键问题。', tag: '目标与约束' },
  { en: 'THE PERSPECTIVE', title: '选择适合问题的视角。', desc: '创业与职业可以结合增长和风险；健康与生活问题优先查专业资料，不强行套用人物观点。', tag: '按问题选择资料' },
  { en: 'THE EVIDENCE', title: '每个重要观点，<br>都要找到来处。', desc: '检索相关材料、阅读上下文，并核对出处、时间、地区和适用人群。', tag: '来源与上下文' },
  { en: 'THE CHALLENGE', title: '让不同的答案<br>互相碰撞。', desc: '主动寻找反例，比较机会与代价。资料有分歧时，把各自的依据摆出来。', tag: '反例与风险' },
  { en: 'THE NEXT STEP', title: '把判断，<br>变成可以行动的一步。', desc: '结合你的约束，比较可选路径，给出下一步以及什么情况会改变结论。', tag: '选择与行动' },
];
const tabs = [...document.querySelectorAll('[data-step]')];
function selectStep(index, focus = false) {
  const step = steps[index];
  tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === index)); tab.tabIndex = i === index ? 0 : -1; });
  document.getElementById('panel').setAttribute('aria-labelledby', `tab-${index}`);
  document.getElementById('step-count').textContent = `0${index + 1} / 05`;
  document.getElementById('step-en').textContent = step.en;
  document.getElementById('step-title').innerHTML = step.title;
  document.getElementById('step-desc').textContent = step.desc;
  document.getElementById('step-tag').textContent = step.tag;
  if (focus) tabs[index].focus();
}
tabs.forEach((tab, i) => {
  tab.addEventListener('click', () => selectStep(i));
  tab.addEventListener('keydown', event => {
    if (!['ArrowRight','ArrowDown','ArrowLeft','ArrowUp','Home','End'].includes(event.key)) return;
    event.preventDefault();
    const index = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (i + (['ArrowRight','ArrowDown'].includes(event.key) ? 1 : -1) + tabs.length) % tabs.length;
    selectStep(index, true);
  });
});
