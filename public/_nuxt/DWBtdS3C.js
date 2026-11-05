const n=(r,u)=>(r=Math.abs(r),u===1||r%10===1&&r%100!==11?0:r%10>=2&&r%10<=4&&(r%100<12||r%100>14)?1:u<3?u-1:2),t=()=>({locale:"en",pluralRules:{ru:n}});export{t as default};
