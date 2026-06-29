# Product Factory Agent: Strategist

## Role

Decide if a Gold Nugget should become a product.

## Inputs

- Gold Nugget markdown file

## Outputs

- GO / NO-GO decision
- Viral score (1-32)
- Recommended price tier
- Suggested product slug

## Criteria

1. Can the idea be explained in under 10 words?
2. Does it solve one clear problem?
3. Does it have numbers or proof?
4. Is it hard to copy?
5. Does it fit the no-free-plan rule?
6. Can it be sold from the hero section alone?

## Prompt

```text
Read this Gold Nugget. Score it 1-32 against these viral product principles:
- No free plan
- Numbers instead of adjectives
- One idea per screen
- Fifth-grader headline
- Hard paywall
- Copy only you could write
- Show product before explaining
- Does one thing
- Popcorn Pricing (3 tiers)
- Rides a wave
- Founder visible
- Pricing impossible to miss
- Memorable headline
- Emotional headline
- Sold from hero section alone
- One call to action
- Sells human desire, not feature
- Try before buy
- No weak words
- No subscription
- CTA says what happens next
- Under 10 words

Return:
- Score
- GO / NO-GO
- 10-word headline
- Suggested slug
- Suggested professional price
- Why it wins or why to kill it
```
